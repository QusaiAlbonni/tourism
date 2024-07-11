from rest_framework.exceptions import APIException

class AdmincantFav(APIException):
    status_code = 400
    default_detail = 'You are admin you cant (add update delete) fav any service'
    default_code = 'Admin_cant_Fav'

class serviceCantReview(APIException):
    status_code = 400
    default_detail = 'this servic cant reviw by any one'
    default_code = 'cant_review_this_service'

class AdmincantReview(APIException):
    status_code = 400
    default_detail = 'You are admin you cant (add update delete) review any service'
    default_code = 'Admin_cant_review'