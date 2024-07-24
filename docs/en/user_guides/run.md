# Train models on standard datasets
This section provides instructions on running the market making pipeline and optimizing the models.
## Prepare dataset
Preparing datasets is also necessary for training. See section [Prepare datasets](preparing_dataset.md) above for details.

## Training the Pipeline

1. Create a Configuration File: Define the training parameters in a configuration file. An example configuration file can be named `configs/parameters/pseudo_marketmaking.yaml`.

2. Run the Training Script: Execute the following command in your terminal, replacing `[path_to_config_file]` with the actual path to your configuration file:

```bash
python run.py -c [path_to_config_file]
```
This command launches the run.py script with the specified configuration file.

3. Additional Training Flags: Refer to the documentation [config](config.md) for details on using additional flags during training. These flags allow for further customization of the training process.

## Runnning Inference only
If you only want to use the trained model for predictions (inference) without retraining (skipping optimization phase), use the following command:
```bash
python run.py -c [path_to_config_file] -o PIPELINE.params.is_optimization=False
```

This command runs the pipeline with the parameters defined in the configuration file but disables the optimization phase (`is_optimization=False`). This means the pipeline will use the pre-trained model for inference without searching for better hyperparameters.