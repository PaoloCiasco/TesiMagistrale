import torch
import torch.nn as nn
from transformers import *
import numpy as np

from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler



class Classifier(nn.Module):
    def __init__(self, model_name, num_labels=2, dropout_rate=0.1):
      super(Classifier, self).__init__()
      # Load the BERT-based encoder
      self.encoder = AutoModel.from_pretrained(model_name)
      # The AutoConfig allows to access the encoder configuration. 
      # The configuration is needed to derive the size of the embedding, which 
      # is produced by BERT (and similar models) to encode the input elements. 
      config = AutoConfig.from_pretrained(model_name)
      self.cls_size = int(config.hidden_size)
      # Dropout is applied before the final classifier
      self.input_dropout = nn.Dropout(p=dropout_rate)
      # Final linear classifier
      self.fully_connected_layer = nn.Linear(self.cls_size,num_labels)

    def forward(self, input_ids, attention_mask):
      # encode all outputs
      model_outputs = self.encoder(input_ids, attention_mask)
      # just select the vector associated to the [CLS] symbol used as
      # first token for ALL sentences
      encoded_cls = model_outputs.last_hidden_state[:,0]
      # apply dropout
      encoded_cls_dp = self.input_dropout(encoded_cls)
      # apply the linear classifier
      logits = self.fully_connected_layer(encoded_cls_dp)
      # return the logits
      return logits, encoded_cls

def make_pred(text, model):

    def generate_data_loader(examples, label_map, tokenizer, do_shuffle = False):
      '''
      Generate a Dataloader given the input examples

      examples: a list of pairs (input_text, label)
      label_mal: a dictionary used to assign an ID to each label
      tokenize: the tokenizer used to convert input sentences into word pieces
      do_shuffle: a boolean parameter to shuffle input examples (usefull in training) 
      ''' 
      #-----------------------------------------------
      # Generate input examples to the Transformer
      #-----------------------------------------------
      input_ids = []
      input_mask_array = []
      label_id_array = []

      # Tokenization 
      for (text, label) in examples:
        # tokenizer.encode_plus is a crucial method which:
        # 1. tokenizes examples
        # 2. trims sequences to a max_seq_length
        # 3. applies a pad to shorter sequences
        # 4. assigns the [CLS] special wor-piece such as the other ones (e.g., [SEP])
        encoded_sent = tokenizer.encode_plus(text, add_special_tokens=True, max_length=512, padding='max_length', truncation=True)
        # convert input word pieces to IDs of the corresponding input embeddings
        input_ids.append(encoded_sent['input_ids'])
        # store the attention mask to avoid computations over "padded" elements
        input_mask_array.append(encoded_sent['attention_mask'])
    
        # converts labels to IDs
        id = -1
        if label in label_map:
          id = label_map[label]
        label_id_array.append(id)

      # Convert to Tensor which are used in PyTorch
      input_ids = torch.tensor(input_ids) 
      input_mask_array = torch.tensor(input_mask_array)
      label_id_array = torch.tensor(label_id_array, dtype=torch.long)
    
      # Building the TensorDataset
      dataset = TensorDataset(input_ids, input_mask_array, label_id_array)

      if do_shuffle:
        # this will shuffle examples each time a new batch is required
        sampler = RandomSampler
      else:
        sampler = SequentialSampler

      # Building the DataLoader
      return DataLoader(
                  dataset,  # The training samples.
                  sampler = sampler(dataset), # the adopted sampler
                  batch_size = 6) # Trains with this batch size.


    #model = torch.load('/home/paoloc/Documents/model_def.pt')
    #model.eval()


    label_list = ['Coronavirus - Focolai RSA/Case di riposo', 'Coronavirus - Focolai familiari/amici', 'Coronavirus - Focolai in altri contesti', 'Coronavirus - Focolai ospedalieri', 'Coronavirus - Focolai scolastico', 'Coronavirus - VARIANTI']

    label_to_id_map = {}
    id_to_label_map = {}
    for (i, label) in enumerate(label_list):
      label_to_id_map[label] = i
      id_to_label_map[i] = label

    tokenizer = AutoTokenizer.from_pretrained("Musixmatch/umberto-commoncrawl-cased-v1")
    nll_loss = torch.nn.CrossEntropyLoss(ignore_index=-1)
    device = torch.device("cpu")


    from sklearn.metrics import classification_report
    from sklearn.metrics import confusion_matrix
    import sys


    def evaluate(dataloader, classifier, print_classification_output=False, print_result_summary=False):

      '''
      Evaluation method which will be applied to development and test datasets.
      It returns the pair (average loss, accuracy)
    
      dataloader: a dataloader containing examples to be classified
      classifier: the BERT-based classifier
      print_classification_output: to log the classification outcomes 
      ''' 
      total_loss = 0
      gold_classes = [] 
      system_classes = []
    
      if print_classification_output:
          print("\n------------------------")
          print("  Classification outcome")
          print("system_label\ttext")
          print("------------------------")

      # For each batch of examples from the input dataloader
      for batch in dataloader:   
        # Unpack this training batch from our dataloader. Notice this is populated 
        # in the method `generate_data_loader`
        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)

        # Tell pytorch not to bother with constructing the compute graph during
        # the forward pass, since this is only needed for backprop (training).
        with torch.no_grad():
          # Each batch is classifed        
          logits, _ = classifier(b_input_ids, b_input_mask)
          # Evaluate the loss. 
          total_loss += nll_loss(logits, b_labels)

        # Accumulate the predictions and the input labels
        _, preds = torch.max(logits, 1)
        system_classes += preds.detach().cpu()
        gold_classes += b_labels.detach().cpu()


        # Print the output of the classification for each input element
        #if print_classification_output:
        for ex_id in range(len(b_input_mask)):
          input_strings = tokenizer.decode(b_input_ids[ex_id], skip_special_tokens=True)
          # convert class id to the real label
          predicted_label = id_to_label_map[preds[ex_id].item()]
          #gold_standard_label = "UNKNOWN"
          # convert the gold standard class ID into a real label
          if b_labels[ex_id].item() in id_to_label_map:
            gold_standard_label = id_to_label_map[b_labels[ex_id].item()]
          # put the prefix "[OK]" if the classification is correct
          #output = '[OK]' if predicted_label == gold_standard_label else '[NO]'
          # print the output
          #print(predicted_label+" ------ "+input_strings)

      # Calculate the average loss over all of the batches.
      avg_loss = total_loss / len(dataloader)
      avg_loss = avg_loss.item()

      # Report the final accuracy for this validation run.
      system_classes = torch.stack(system_classes).numpy()
      gold_classes = torch.stack(gold_classes).numpy()
      accuracy = np.sum(system_classes == gold_classes) / len(system_classes)

      if print_result_summary:
        print("\n------------------------")
        print("  Summary")
        print("------------------------")
        #remove unused classes in the test material
        filtered_label_list = []
        for i in range(len(label_list)):
          if i in gold_classes:
            filtered_label_list.append(id_to_label_map[i])
        print(classification_report(gold_classes, system_classes, digits=3, target_names=filtered_label_list))

        print("\n------------------------")
        print("  Confusion Matrix")
        print("------------------------")
        conf_mat = confusion_matrix(gold_classes, system_classes)
        for row_id in range(len(conf_mat)):
          print(filtered_label_list[row_id]+"\t"+str(conf_mat[row_id]))

      return avg_loss, accuracy, predicted_label


    # Let us select a simple example
    my_test = text
    label = "_"


    # Let us convert it in a pair that can be used to populate a dataloader...
    my_list = [(my_test,label)]
    my_data_loader = generate_data_loader(my_list, label_to_id_map, tokenizer)

    # ... and reuse the evaluate method
    _, _, label_predicted = evaluate(my_data_loader, model, print_classification_output = False)

    return label_predicted

