import os
import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


try:
    # Get the Tencent Cloud credentials from environment variables   
    cred = credential.Credential(os.getenv("TENCENTCLOUD_SECRET_ID"), os.getenv("TENCENTCLOUD_SECRET_KEY"))
    #
    httpProfile = HttpProfile()
    httpProfile.endpoint = "ocr.tencentcloudapi.com"

    # Instantiate a client option, optional, can be skipped if there are no special requirements
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # Instantiate the client object for the product to be requested, clientProfile is optional
    client = ocr_client.OcrClient(cred, "", clientProfile)

    # Instantiate a request object, each interface corresponds to a request object
    req = models.RecognizeGeneralInvoiceRequest()
    params = {
        "ImageUrl": "http://111.229.40.154/example/download?fileName=statestreet_invoice_25337000000315751962.pdf&folder=onboard",
        "EnablePdf": True
    }
    req.from_json_string(json.dumps(params))

    # The returned resp is an instance of RecognizeGeneralInvoiceResponse, corresponding to the request object
    resp = client.RecognizeGeneralInvoice(req)
    # Output the response in JSON format
    print(resp.to_json_string())

except TencentCloudSDKException as err:
    print(err)