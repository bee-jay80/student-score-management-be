



# JWT Cookies Utility
def set_jwt_cookie_and_response(response, access, refresh):
    response["access_token"] = access
    
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="None",
        secure=True,
    )


# Pending Verification Cookie
def set_pending_cookie(response, pending_token):
    response.set_cookie(
        key="verification_session",
        value=pending_token,
        httponly=True,
        samesite="None",
        max_age=900,  # 15 mins
        secure=True,
    )