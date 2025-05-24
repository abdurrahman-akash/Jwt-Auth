from rest_framework import status
from rest_framework.response import Response


def success_response(msg,data):
    statuscode = status.HTTP_200_OK
    response = {
        "statuscode" : statuscode,
        "detail" : msg,
        "error" : "",
        "data" : data
    }
    return Response(response,status=statuscode)

def error_response(msg,data):
    statuscode = status.HTTP_400_BAD_REQUEST
    response = {
        "statuscode" : statuscode,
        "detail" : msg,
        "error" : msg,
        "data": data
    }
    return Response(response,status=statuscode)


def s_404(reason):

    return Response({'error':f'{reason} Does not Exist'},status=status.HTTP_404_NOT_FOUND)


def s_406(reason):

    return Response({'error':f'Except {reason} into Request Body'},status=status.HTTP_406_NOT_ACCEPTABLE)



def s_200(ser):

    return Response(ser.data, status=status.HTTP_200_OK)