import json, random
from typing import List, Union
from fastapi import APIRouter, HTTPException, status, Path, Form
from app.database import (select_dashboard_data, )
from pathlib import Path


router = APIRouter()


# @router.get('/', status_code=status.HTTP_200_OK)
# async def get_dashboard_data():
#     try:
#         return select_dashboard_data()
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f'Error {e}'
#         )
    
#http://127.0.0.1:8000/dashboard/?filterAccountBookDateDocFrom=2023-06-01&filterAccountBookDateDocTo=2023-08-01&filterAccountBookDateEnterFrom=2023-06-01&filterAccountBookDateEnterTo=2023-08-01&filterReportVehicleDateEnterFrom=2023-06-01&filterReportVehicleDateExitTo=2023-08-01

BASE_DIR = Path(__file__).resolve().parent.parent.parent
users_file = BASE_DIR / 'data/users/users_list.json'
TOKEN_LIST = list()


try:
    #  при отсутствии файла с пользователями вход без страницы аутентификации
    with open(users_file, 'r') as jsonfile:
        USERS_LIST = json.load(jsonfile)  # type = dict
    IS_AUTH_REQUIRED = True
    # IS_AUTHORIZED = False
    print('THE FILE HAS FOUNDED, AUTH IS REQUIRED!', USERS_LIST)
except FileNotFoundError:
    IS_AUTH_REQUIRED = False
    # IS_AUTHORIZED = True
    print('THE FILE HAS NOT FOUNDED, AUTH IS NOT REQUIRED!')


@router.post('/signin', status_code=status.HTTP_202_ACCEPTED)
async def user_sign_in(
    login: Union[str, None] = None,
    password: Union[str, None] = None,
):
    # user authentification
    # global IS_AUTHORIZED
    
    # print(f'!!!!!! post request = *{login}* *{password}*') ######

    if not IS_AUTH_REQUIRED:
        return {'message': 'authorization is not required'}
    
    # if IS_AUTH_REQUIRED and IS_AUTHORIZED:
    #     return {'message': 'authorization has already done'}

    if (not login) or (not password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
        )
        
    if login in USERS_LIST and USERS_LIST[login] == password:
        # IS_AUTHORIZED = True

        new_token = str(random.randint(1, 1000000))
        TOKEN_LIST.append(new_token)
        # print('new_token, TOKEN_LIST =', new_token, TOKEN_LIST) ##

        # return {'user': login}
        return {'your_new_token': new_token}
    else:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
        )
    

@router.post('/signout', status_code=status.HTTP_200_OK)
async def user_sign_out(
    token: Union[str, None] = None,
):
    # user sign out
    # global IS_AUTHORIZED

    if IS_AUTH_REQUIRED:
        # IS_AUTHORIZED = False
        
        # print('token =', token)  ## 
        TOKEN_LIST.remove(token)
        # print('removed, updated TOKEN_LIST =', TOKEN_LIST)  ##
        
        return {'message': 'signed out'}
    else:
        return {'message': 'there was not an authorization'}


@router.get('/', status_code=status.HTTP_200_OK)
async def get_dashboard_data_filtered(
        token: Union[str, None] = None,
        filterAccountBookDateDocFrom: Union[str, None] = None,
        filterAccountBookDateDocTo: Union[str, None] = None,
        filterAccountBookDateEnterFrom: Union[str, None] = None,
        filterAccountBookDateEnterTo: Union[str, None] = None,
        filterReportVehicleDateEnterFrom: Union[str, None] = None,
        filterReportVehicleDateExitTo: Union[str, None] = None,
        ):
    
    if IS_AUTH_REQUIRED and (not token or token not in TOKEN_LIST):
        raise HTTPException(
            status_code=401,
            detail='Unauthorized',
        )
    
    # if IS_AUTH_REQUIRED and (not IS_AUTHORIZED):
    #     raise HTTPException(
    #         status_code=401,
    #         detail='Unauthorized',
    #     )
    
    # return {'message': 'ok! data is received'}

    try:
        filters = {
            "filterAccountBookDateDocFrom": filterAccountBookDateDocFrom,
            "filterAccountBookDateDocTo": filterAccountBookDateDocTo,
            "filterAccountBookDateEnterFrom": filterAccountBookDateEnterFrom,
            "filterAccountBookDateEnterTo": filterAccountBookDateEnterTo,
            "filterReportVehicleDateEnterFrom": filterReportVehicleDateEnterFrom,
            "filterReportVehicleDateExitTo": filterReportVehicleDateExitTo,
                }

        return select_dashboard_data(
            #selects_keys_list=['received_product_quantity', 'received_dt_quantity', 'received_tnved_quantity', 'account_book', 'report_vehicle'], 
            filters=filters)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Error {e}'
        )
    #'received_product_quantity', 'received_dt_quantity', 'received_tnved_quantity', 