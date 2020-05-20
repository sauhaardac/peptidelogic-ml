import logging

import torch

import mousenet as mn

logging.getLogger().setLevel(logging.DEBUG)  # Log all info

import os

if os.name == 'nt':
    dlc = mn.DLCProject(config_path='D:\Peptide Logic\Writhing\config.yaml', pcutoff=0.25)

    labeled_videos = mn.json_to_videos(r'D:\Peptide Logic\Writhing', '../benv2-synced.json', mult=1)

else:
    dlc = mn.DLCProject(config_path='/home/pl/sauhaarda/peptide_logic_refactored/dlc/'
                                    'mouse_behavior_id-sauhaarda-2020-01-24/config.yaml', pcutoff=0.25)
    labeled_videos = mn.json_to_videos('/home/pl/Data', '../benv2-synced.json', mult=1)

# Infer trajectories
dlc.infer_trajectories(labeled_videos)

# Define hyperparameters
writhing_hparams = {'num_filters': (7, (1, 20)),
                    'num_filters2': (11, (1, 20)),
                    'filter_width': (71, (11, 101, 10)),  # must be an odd number
                    'filter_width2': (91, (11, 101, 10)),  # must be an odd number
                    'in_channels': 6,  # number of network inputs
                    'weight': 7,  # how much "emphasis" to give to positive labels
                    'loss': torch.nn.functional.binary_cross_entropy,
                    'train_val_split': 1.0}

itching_hparams = {'num_filters': (15, (1, 20)),
                   'num_filters2': (7, (1, 20)),
                   'filter_width': (21, (11, 101, 10)),  # must be an odd number
                   'filter_width2': (61, (11, 101, 10)),  # must be an odd number
                   'in_channels': 6,  # number of network inputs
                   'weight': 7,  # how much "emphasis" to give to positive labels
                   'loss': torch.nn.functional.binary_cross_entropy,
                   'train_val_split': 1.0}

hparams = itching_hparams


# Define Network Input
def df_map(df):
    df['head', 'x'] = (df['leftear']['x'] + df['rightear']['x']) / 2
    df['head', 'y'] = (df['leftear']['y'] + df['rightear']['y']) / 2
    body_length = mn.dist(df, 'head', 'tail')
    x = [mn.dist(df, 'leftpaw', 'tail'), mn.dist(df, 'rightpaw', 'tail'), mn.dist(df, 'neck', 'tail'), body_length,
         df['leftpaw']['likelihood'], df['rightpaw']['likelihood']]
    return x


# Define Network Architecture
class MouseModel(torch.nn.Module):
    def __init__(self, params):
        super().__init__()
        self.conv1 = torch.nn.Conv1d(params.in_channels, params.num_filters, kernel_size=params.filter_width,
                                     padding=(params.filter_width - 1) // 2)
        self.conv2 = torch.nn.Conv1d(params.num_filters, params.num_filters2, kernel_size=params.filter_width2,
                                     padding=(params.filter_width2 - 1) // 2)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x, _ = torch.max(x, dim=1)
        return torch.sigmoid(x)


torch.manual_seed(1)  # consistent behavior w/ random seed
dataset = mn.DLCDataset(labeled_videos, df_map, behavior='Itch')

runner = mn.Runner(MouseModel, hparams, dataset)
# runner.hyperparemeter_optimization(timeout=600)

# print(dataset[0][0].shape)
model, auc = runner.train_model(max_epochs=500)
print(auc)

# Run visualization
# model.eval()
# model.cpu()
# model_out = model(dataset[0][0]).detach()  # get model output
# dlc.create_labeled_videos(labeled_videos)  # create labeled video if it doesn't exist
# # print(f"{model_out[0].max()} {model_out[0].min()}")
# #


# vid = 0
# mx, my = dataset[0]
# print(my.shape)
# plt.plot(list(range(len(my[vid]))), my[vid], color='red')
# # plt.plot(list(range(len(my[vid]))), model_out[vid], color='blue')
# plt.savefig('PLOT.png')


# #
# pickle.dump((dataset[0][1], model_out), open('vis.pkl', 'wb'))
# #
# for video, y, y_hat in zip(labeled_videos, dataset[0][1], model_out):
#     mn.VisualDebugger(video, y, y_hat)
#     break  # only visualize first video for now
