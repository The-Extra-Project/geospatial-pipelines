"""
referenced implementation from daggle-xyz: 

it consist of taking user requests in REST format and then scheduling the compute from the dockerhub based instance to the user account.
"""

from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from bacalhau_sdk.api import submit, results, states
from bacalhau_sdk.config import get_client_id
from bacalhau_apiclient.models.storage_spec import StorageSpec
from bacalhau_apiclient.models.spec import Spec
from bacalhau_apiclient.models.job_spec_language import JobSpecLanguage
from bacalhau_apiclient.models.job_spec_docker import JobSpecDocker
from bacalhau_apiclient.models.publisher_spec import PublisherSpec
from bacalhau_apiclient.models.deal import Deal



app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware, allow_origins="*", allow_methods="*", allow_headers="*"
)

router = APIRouter(
    prefix="/bacalhau",
    responses={404: {"message": "Not found"}},
)


app.include_router(router)



@router.post("/neuralangelo/submit")
async def schedule_job(request: Request, response: Response):
    try:
        params = await request.json()
        if "jobspecdocker" or "storagespec"  not in params:
            raise Exception("Please send valid body.")
        inputs = []
        for input in params["storagespec"]:
            print("input job params are" + input)
            inputs.append(StorageSpec(**input))
 
        data = dict(
            APIVersion="V1beta1",
            ClientID=get_client_id(),
            Spec=Spec(
                engine="Docker",
                verifier="Noop",
                publisher_spec=PublisherSpec(type="Estuary"),
                inputs=inputs,
                docker=JobSpecDocker(**params["jobspecdocker"]),
                language=JobSpecLanguage(job_context=None),
                wasm=None,
                resources=None,
                # timeout=1800,
                outputs=[
                    StorageSpec(
                        storage_source="IPFS",
                        name="outputs",
                        path="/outputs",
                    )
                ],
                deal=Deal(concurrency=1, confidence=0, min_bids=0),
                do_not_track=False,
            ),
        )
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}



@router.get("/neuralangelo/state/{job_id}")
async def get_job(job_id: str, response: Response):
    try:
        if job_id is None:
            raise Exception("Please send a job id.")

        result = states(job_id=job_id)
        return result
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}


@app.get("/neuralangelo")
def base_scheduler():
    return {"connection to bacalhau instance complete"}
