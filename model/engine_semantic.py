from tqdm import tqdm
import torch
import numpy as np


def train_semantic(
        model,
        train_dataloader,
        device,
        optimizer,
        processor,
        metric,
        num_classes=2
):
    print('Training semantic')
    model.train()
    train_running_loss = []

    prog_bar = tqdm(
        train_dataloader,
        total=len(train_dataloader),
        bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'
    )

    for i, batch in enumerate(prog_bar):
        optimizer.zero_grad()

        # print(batch['mask_labels'])
        # print(batch['class_labels'])
        outputs = model(
            pixel_values=batch['pixel_values'].to(device),
            mask_labels=[mask_label.to(device) for mask_label in batch['mask_labels']],
            class_labels=[class_label.to(device) for class_label in batch['class_labels']],
            pixel_mask=batch['pixel_mask'].to(device)
        )

        ##### BATCH-WISE LOSS #####
        loss = outputs.loss
        train_running_loss.append(loss.item())
        ###########################

        ##### BACKPROPAGATION AND PARAMETER UPDATION #####
        loss.backward()
        optimizer.step()
        ##################################################

        target_sizes = [(image.shape[1], image.shape[2]) for image in batch['orig_images']]
        pred_maps = processor.post_process_semantic_segmentation(
            outputs, target_sizes=target_sizes
        )
        pred_maps_un = []
        batch_un = []
        for pr_map in pred_maps:
            pred_maps_un.append(np.unique(pr_map))
        for bt in batch['orig_masks']:
            batch_un.append(np.unique(bt))
        print(f"pred {pred_maps_un}")
        print(f"bt {batch_un}")
        ###########################
        metric.add_batch(references=batch['orig_masks'], predictions=pred_maps)

    ##### PER EPOCH LOSS #####
    train_loss = sum(train_running_loss) / len(train_running_loss)
    # , reduce_labels=True
    metric = metric.compute(num_labels=num_classes, ignore_index=255)
    return train_loss, metric


def validate_semantic(
        model,
        train_dataloader,
        device,
        processor,
        metric,
        num_classes=2
):
    print('Validation semantic')
    model.train()
    train_running_loss = []

    prog_bar = tqdm(
        train_dataloader,
        total=len(train_dataloader),
        bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'
    )

    for i, batch in enumerate(prog_bar):
        # print(batch['mask_labels'])
        # print(batch['class_labels'])
        outputs = model(
            pixel_values=batch['pixel_values'].to(device),
            mask_labels=[mask_label.to(device) for mask_label in batch['mask_labels']],
            class_labels=[class_label.to(device) for class_label in batch['class_labels']],
            pixel_mask=batch['pixel_mask'].to(device)
        )

        ##### BATCH-WISE LOSS #####
        loss = outputs.loss
        train_running_loss.append(loss.item())
        ###########################

        target_sizes = [(image.shape[1], image.shape[2]) for image in batch['orig_images']]
        pred_maps = processor.post_process_semantic_segmentation(
            outputs, target_sizes=target_sizes
        )
        pred_maps_un = []
        batch_un = []
        for pr_map in pred_maps:
            pred_maps_un.append(np.unique(pr_map))
        for bt in batch['orig_masks']:
            batch_un.append(np.unique(bt))
        print(f"pred {pred_maps_un}")
        print(f"bt {batch_un}")
        ###########################
        metric.add_batch(references=batch['orig_masks'], predictions=pred_maps)

    ##### PER EPOCH LOSS #####
    train_loss = sum(train_running_loss) / len(train_running_loss)
    # , reduce_labels=True
    metric = metric.compute(num_labels=num_classes, ignore_index=255)
    return train_loss, metric
