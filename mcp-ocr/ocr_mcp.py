
import os
from typing import Optional, Dict, List, Any
import httpx
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ocr.v20181119 import ocr_client, models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("OCR Service")

@mcp.tool()
async def invoice_ocr(
    image_url: str,
    enable_pdf: bool = True
) -> Dict[str, Any]:
    """
    Recognize general invoice from an URL.
    This URL can be image or PDF file.
    
    :param image_url: URL of the image to be processed.
    :param enable_pdf: Whether to enable PDF processing.
    :return: Response from the OCR service.
    """
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
            "ImageUrl": image_url,
            "EnablePdf": enable_pdf
        }
        req.from_json_string(json.dumps(params))

        # The returned resp is an instance of RecognizeGeneralInvoiceResponse, corresponding to the request object
        resp = client.RecognizeGeneralInvoice(req)
        # Output the response in JSON format
        print(resp.to_json_string())
        return resp.to_json_string()
    except TencentCloudSDKException as err:
        print(err)
        return resp.to_json_string()
    
    except httpx.HTTPStatusError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Configure CORS middleware
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id"]  # for SSE support
        )
    ]

    # Run the MCP server in HTTP SSE mode
    mcp.run(
        transport="streamable-http", 
        host="0.0.0.0", 
        port=8000, 
        path="/mcp",
        middleware=middleware
    )