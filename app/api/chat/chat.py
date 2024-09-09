# python inner 
import ast
import logging

# fastapi
from fastapi import FastAPI, APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_jwt_auth import AuthJWT

# app
from payload.chat_payload import *
from .helper import make_question_from_files, get_prompt_from_mongo
from utils.constants import AIREPORT_LIST

# llm module
from module.langchain import RunLLM

# helper
from helper import *



question = APIRouter(prefix="/llm")



@question.post("/activate")
async def ask(payload: chatPayloadModel, Authorize: AuthJWT = Depends(), file: UploadFile = File()):
    """Ask Question and get 'STREAM' Answer"""
    try:
        session_key = Authorize.get_jwt_subject()
        model = payload.model
        path_name = payload.pathName
        data_type = payload.dataType
        prompt = payload.prompt
        info = payload.info

        if data_type:
            files = await file.read()
            question, filename = make_question_from_files(files)
        else:
            question = prompt
            filename = None

        # Run LLM
        args = {
            "model_version": model,
            "pathName": path_name,
            "question": question,
            "filename": filename,
            "session_key": session_key,
        }

        response = RunLLM(args=args).execute()
        return StreamingResponse(response, media_type='text/plain')
    
    except Exception as e:
        logging.info(e)
        return StreamingResponse()