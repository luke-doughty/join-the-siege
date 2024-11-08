# Heron Coding Challenge - File Classifier - Luke Doughty Submission

## About this code

This code fundamentally revolves around the Hugging Face [Text Inference](https://huggingface.co/docs/transformers/v4.46.2/en/main_classes/pipelines#transformers.TextClassificationPipeline) and [Image Inference](https://huggingface.co/docs/transformers/v4.46.2/en/main_classes/pipelines#transformers.ZeroShotImageClassificationPipeline) to determine a files classification.

My solution tries to use the least amount of inference possible before having to use any more. As such I do a Zero Shot classification on the file name, as we should hope files are either named correctly, or randomly, not incorrectly (i.e a bank statement named `drivers_license.jpg`). If this doesnt meet the highest confidence threshold, we then go into two different classifiers depending on the file type with lower confidence thresholds.

I use NLP inference at least once in each request as it allows for scalability with different industries and file types, instead of coding custom logic per new item accepted. This is a worthy trade off however, as loading the model weights is done on startup of the code, not per request, which in a kubernetes deployment would mean only on pod creation.

Below is the classification path of the two file types, in descending priority:

# Image:

1. Compare file name against latest (Bart)[https://huggingface.co/facebook/bart-large-mnli] model

2. Compare image content against the latest (SigLIP)[https://huggingface.co/google/siglip-so400m-patch14-384] model

3. If file name passes the failsafe value, use this

4. Return Classification Unknown

# File:

1. Compare file name against latest (Bart)[https://huggingface.co/facebook/bart-large-mnli] model

2. Compare file content against latest (Bart)[https://huggingface.co/facebook/bart-large-mnli] model

3. Take the highest of the two that pass the fail safe

4. Return Classification Unknown

# Assumptions

I have worked on the basis that file names _should_ be treated primarily as correct over file contents, but also because of this, they are judged more strictly.

I have also developed this with thought that it would be scaled up across multiple pods in a kubernetes cluster, meaning it could handle as many requests concurrently as there are pods. This also allows for the use of larger language and image inference models that have been used here.

For deployment in a smaller environement or on a limited capability dev machine, I would recommend using the (Base SigLIP)[https://huggingface.co/google/siglip-base-patch16-224] model for image inference and (Base Bart)[https://huggingface.co/facebook/bart-base] for text inference. Be aware though, this will produce different results, and pass rates would need to be adjusted accordingly. If the machine this is being run on is using a GPU, this can be set in the pipeline setup in `classifier.py`.

## Building an image

To build an image run `docker build . -t ${IMAGE_NAME}` from the root directory. This is also ran automatically when merging a PR to to master, with the image being pushed to my docker hub registry.

## To run locally:

1. Install dependencies:

   ```shell
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the Flask app:

   ```shell
   python -m src.app
   ```

3. Configure the catagories you want to classify in `classifer_catagories.json`

4. Test the classifier using a tool like curl:

   ```shell
   curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1:5000/classify_file
   ```

5. Run tests:
   ```shell
    pytest
   ```

## To deploy in a cluster

1. Setup a kubernetes cluster

2. Configure `classifier.tf` so that the code below points to your cluster:

   ```
   provider "kubernetes" {
        config_path = "~/.kube/config"
   }
   ```

3. Set the amount of replicas you would like, following the format `replicas = 3`

4. Finally configure the catagories you want to classify in `classifer_catagories.json`

5. Use terraform to apply with the latest image
