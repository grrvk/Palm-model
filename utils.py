import os
import numpy as np
import matplotlib.pyplot as plt
from transformers import (Mask2FormerForUniversalSegmentation,
                          Mask2FormerImageProcessor)


def load_model(device, model_type, folder_name='out', name='model_out'):
    path = os.path.join(folder_name, f"{model_type}_{name}")
    model = Mask2FormerForUniversalSegmentation.from_pretrained(
        os.path.join(path, 'final_model')
    ).to(device)

    processor = Mask2FormerImageProcessor.from_pretrained(
        os.path.join(path, 'final_processor')
    )

    return model, processor


def save_model(model, processor, model_type, folder_name='out', name='model_out'):
    out_dir = os.path.join(folder_name, f"{model_type}_{name}")
    out_final_model = os.path.join(out_dir, 'final_model')
    out_final_processor = os.path.join(out_dir, 'final_processor')

    os.makedirs(folder_name, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_final_model, exist_ok=True)
    os.makedirs(out_final_processor, exist_ok=True)

    processor.do_normalize = True
    processor.do_resize = True
    processor.do_rescale = True

    model.save_pretrained(out_final_model)
    processor.save_pretrained(out_final_processor)


def draw_plot(model_type, x, train_values, val_values, ylabel, out_dir):
    plt.plot(x, train_values, label=f'train {ylabel}')
    plt.plot(x, val_values, label=f'validation {ylabel}')
    plt.xlabel("epoch")
    plt.ylabel(f"{ylabel}")
    plt.title(f"Train/validation {ylabel}")
    plt.legend()
    plt.savefig(os.path.join(out_dir, f'{model_type}_{ylabel}.png'))
    plt.clf()


def plot_loss_miou(model_type, epochs, train_loss, valid_loss, train_miou, valid_miou, folder_name='out'):
    os.makedirs(folder_name, exist_ok=True)
    out_dir = os.path.join(folder_name)

    x = np.arange(1, epochs+1)
    draw_plot(model_type, x, train_loss, valid_loss, 'loss', out_dir)
    draw_plot(model_type, x, train_miou, valid_miou, 'miou', out_dir)


def dump_metrics_log(model_type, epoch, timestamp, metrics_data, folder_name='out'):
    os.makedirs(folder_name, exist_ok=True)
    out_dir = os.path.join(folder_name)

    file = open(os.path.join(out_dir, f"{model_type}_metrics.txt"), "a")
    file.write(f"EPOCH {epoch} ------ {timestamp}\n")
    file.write('Train\n')
    file.write(str(metrics_data['train']))
    file.write('\nValidation\n')
    file.write(str(metrics_data['validation']))
    file.write("\n")
    file.close()


def delete_metrics(model_type, folder_name='out'):
    out_dir = os.path.join(folder_name)
    path = os.path.join(out_dir, f"{model_type}_metrics.txt")
    if os.path.exists(path):
        os.remove(path)
        print(f'Previous {model_type}_metrics.txt deleted')


