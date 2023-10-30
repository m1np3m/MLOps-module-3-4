# Ref: https://docs.bentoml.org/en/latest/quickstarts/deploy-a-yolo-model-with-bentoml.html
import bentoml
import pandas as pd
from alibi_detect.saving import load_detector
from bentoml.io import JSON
from bentoml.exceptions import InternalServerError

import constants.vae as vae_constants
from logs.logger import bentoml_logger
from models.model import TCPConnection


class AnomalyDetectionRunner(bentoml.Runnable):
    SUPPORTED_RESOURCES = "cpu"  # Specify ("nvidia.com/gpu", "cpu") if GPU is supported
    SUPPORTS_CPU_MULTI_THREADING = True  # Support multi-threading for this model

    def __init__(self):
        self.model = load_detector(vae_constants.WEIGHTS_PATH)
        self.return_instance_score = True

    # We set batchable to False since it has effects
    # only with numpy arrays and pandas series, etc.
    # https://docs.bentoml.org/en/latest/guides/batching.html#custom-batching
    @bentoml.Runnable.method(batchable=False)
    def inference(self, input_data):
        # Convert dict to a numpy array
        processed_input = pd.DataFrame(input_data.dict(), index=[0]).to_numpy()

        # Debug input data
        bentoml_logger.info("Input data:")
        bentoml_logger.info(processed_input)
        bentoml_logger.info("Input shape:")
        bentoml_logger.info(processed_input.shape)

        # Return prediction
        pred = self.model.predict(
            processed_input,
            return_instance_score=vae_constants.RETURN_INSTANCE_SCORE,
            return_feature_score=vae_constants.RETURN_FEATURE_SCORE,
        )

        # Debug output result
        if not isinstance(pred, pd.DataFrame):
            raise InternalServerError("Output format is not invalid")
        
        bentoml_logger.info("Prediction result:")
        bentoml_logger.info(pred)

        return pred


# Create a runner object
ad_runner = bentoml.Runner(AnomalyDetectionRunner)

# Create BentoML service
svc = bentoml.Service("anomaly_detection_with_exceptions_demo", runners=[ad_runner])


# Create our API with route /invocation
# which receive an input, which is parsed to Pandas DataFrame by BentoML,
# and so is the output
@svc.api(input=JSON(pydantic_model=TCPConnection), output=JSON())
async def detection_with_exceptions(input_data):
    with bentoml.monitor("intrusion_detection") as mon:
        mon.log(input_data.dict(), name="record", role="", data_type="")

    # Runners are executed in a asynchronous manner
    pred = await ad_runner.inference.async_run(input_data)
    return pred
