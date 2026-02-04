



# JWT Cookies Utility
def set_jwt_cookies(response, access, refresh):
    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        samesite="Lax",
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        samesite="Lax",
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