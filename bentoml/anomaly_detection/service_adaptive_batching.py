# Ref: https://docs.bentoml.org/en/latest/quickstarts/deploy-a-yolo-model-with-bentoml.html
import bentoml
from alibi_detect.saving import load_detector
from bentoml.io import JSON, NumpyNdarray

import constants.vae as vae_constants
from logs.logger import bentoml_logger


class AnomalyDetectionRunner(bentoml.Runnable):
    SUPPORTED_RESOURCES = "cpu"  # Specify ("nvidia.com/gpu", "cpu") if GPU is supported
    SUPPORTS_CPU_MULTI_THREADING = True  # Support multi-threading for this model

    def __init__(self):
        self.model = load_detector(vae_constants.WEIGHTS_PATH)
        self.return_instance_score = True

    # We set batchable to True here, with inputs will 
    # be batched along the 0th dimension
    @bentoml.Runnable.method(batchable=True, batch_dim=0)
    def inference(self, inputs_data):
        # processed_data = np.array(inputs_data)
        processed_data = inputs_data

        # Debug input data
        bentoml_logger.info("Processed data:")
        bentoml_logger.info(processed_data)

        # Return prediction
        pred = self.model.predict(
            processed_data,
            return_instance_score=vae_constants.RETURN_INSTANCE_SCORE,
            return_feature_score=vae_constants.RETURN_FEATURE_SCORE,
        )

        # Debug output result
        bentoml_logger.info("Prediction result:")
        bentoml_logger.info(pred["data"]["is_outlier"])

        # We can not use JSON directly here because the output
        # is required to be iterable, so we can use pred["data"]["is_outlier"]
        # to return a numpy array or use the trick as the below
        return [pred]


# Create a runner object
ad_runner = bentoml.Runner(AnomalyDetectionRunner)

# Create BentoML service
svc = bentoml.Service("anomaly_detection_adaptive_batching_demo", runners=[ad_runner])


# Create our API with route /invocation
# which receive an input, which is parsed to Pandas DataFrame by BentoML,
# and so is the output
@svc.api(input=NumpyNdarray(), output=JSON())
async def detection_adaptive_batching(input_data):
    # Runners are executed in a asynchronous manner
    pred = await ad_runner.inference.async_run([input_data])
    return pred
