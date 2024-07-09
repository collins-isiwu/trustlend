from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = ''
API_URL = '/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "TrustLend API Documentation"
    }
)

swagger_blueprint = Blueprint('swagger', __name__)

@swagger_blueprint.route(API_URL)
def swagger_spec():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "TrustLend API",
            "description": "API documentation for TrustLend application",
            "version": "1.0.0",
        },
        "tags": [
            {
                "name": "User",
                "description": "User related endpoints"
            },
            {
                "name": "Verification",
                "description": "Verification related endpoints"
            },
            {
                "name": "RequestLoan",
                "description": "Request Loan related endpoints"
            },
            {
                "name": "Loan",
                "description": "Loan related endpoints"
            }
        ],
        "paths": {
            "/api/v1/user/register": {
                "post": {
                    "tags": ["User"],
                    "summary": "Register a new user",
                    "description": "Creates a new user account",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/UserRegister"
                        }
                    }],
                    "responses": {
                        "201": {
                            "description": "User registered successfully",
                            "schema": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "409": {
                            "description": "User already exists",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/api/v1/user/sign-in": {
                "post": {
                    "tags": ["User"],
                    "summary": "User login",
                    "description": "Authenticates a user and returns access and refresh tokens",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/UserLogin"
                        }
                    }],
                    "responses": {
                        "200": {
                            "description": "User logged in successfully",
                            "schema": {
                                "$ref": "#/definitions/Tokens"
                            }
                        },
                        "401": {
                            "description": "Invalid credentials",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/api/v1/user/token/refresh": {
                "post": {
                    "tags": ["User"],
                    "summary": "Refresh access token",
                    "description": "Generates a new access token using the refresh token",
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <refresh_token>"
                    }],
                    "responses": {
                        "200": {
                            "description": "Access token refreshed",
                            "schema": {
                                "$ref": "#/definitions/Token"
                            }
                        },
                        "401": {
                            "description": "Invalid or expired refresh token",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/api/v1/user/logout": {
                "post": {
                    "tags": ["User"],
                    "summary": "Logout user",
                    "description": "Logs out the user by blacklisting the refresh token",
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <access_token>"
                    }],
                    "responses": {
                        "200": {
                            "description": "User logged out successfully",
                            "schema": {
                                "$ref": "#/definitions/Success"
                            }
                        },
                        "401": {
                            "description": "Invalid or expired access token",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/api/v1/user/detail": {
                "get": {
                    "tags": ["User"],
                    "summary": "Get user details",
                    "description": "Fetches details of the currently logged-in user",
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    }],
                    "responses": {
                        "200": {
                            "description": "User details retrieved successfully",
                            "schema": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "404": {
                            "description": "User not found",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                },
                "put": {
                    "tags": ["User"],
                    "summary": "Update user details",
                    "description": "Updates details of the currently logged-in user",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/UserUpdate"
                        }
                    }],
                    "responses": {
                        "200": {
                            "description": "User details updated successfully",
                            "schema": {
                                "$ref": "#/definitions/User"
                            }
                        },
                        "400": {
                            "description": "Validation error",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        },
                        "404": {
                            "description": "User not found",
                            "schema": {
                                "$ref": "#/definitions/Error"
                            }
                        }
                    }
                }
            },
            "/api/v1/verification": {
                "get": {
                    "tags": ["Verification"],
                    "summary": "Get User Verification Status",
                    "description": "Checks whether a user submitted verification form before and returns User is verified if Admin has approved verification credentials or User is not verified",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    }],
                    "responses": {
                        "200": {
                            "description": "User is verified!' if verification.is_verified else 'User is not verified!",
                            "schema": {
                                "$ref": "#/definitions/Verification"
                            }
                        },
                        "404": {
                            "description": "No user found with the given ID",
                        },
                        "404": {
                            "description": "Verification status not found.",
                        }
                    }
                },
                "patch": {
                    "tags": ["Verification"],
                    "summary": "Verify Users. Admins only",
                    "description": "Verifies user by changing is_verified to True. This endpoint is protected for admins only.",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    }],
                    "responses": {
                        "200": {
                            "description": "Verification Complete!",
                        },
                        "404": {
                            "description": "No user found with the given ID",
                        },
                        "404": {
                            "description": "User has not requested for verification.",
                        },
                        "208": {
                            "description": "User already approved!",
                        },
                        "400": {
                            "description": "Verification not approved!",
                        },

                    }
                },
                "post": {
                    "tags": ["Verification"],
                    "summary": "Request Verification",
                    "description": "User can request verification by submitting verification credientals.",
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    },{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Verification"
                        }
                    }],
                    "responses": {
                        "201": {
                            "description": "Verification request has been created",
                            "schema": {
                                "$ref": "#/definitions/Verification"
                            }
                        },
                        "404": {
                            "description": "No user found with the given ID",
                        },
                        "400": {
                            "description": "Verification request already exists.",
                        }
                    }
                },
            },
             # Loan endpoints
            "/api/v1/loan/request/{request_loan_id}": {
                "get": {
                    "tags": ["RequestLoan"],
                    "summary": "Retrieve Request Loan by ID",
                    "description": "Returns a single loan",
                    "parameters": [{
                            "name": "request_loan_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "format": "int64",
                            "description": "ID of request loan to retrieve"},{
                            "name": "Authorization",
                            "in": "header",
                            "required": True,
                            "type": "string",
                            "description": "Bearer <JWT>"}
                    ],
                    "responses": {
                        "200": {
                            "description": "Request Loan retrieved!",
                        },
                        "404": {
                            "description": "Request Loan Not Found!",
                        },
                    }
                },
            },
            "/api/v1/loan/request": {
                "post": {
                    "tags": ["RequestLoan"],
                    "summary": "Create Loan Request",
                    "description": "Creates loan request",
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    },{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/Requestloan"
                        }
                    }],
                    "responses": {
                        "201": {
                            "description": "Loan request created!",
                        },
                        "404": {
                            "description": "No user found with the given ID",
                        },
                        "404": {
                            "description": "Request Loan Not Found!",
                        },
                        "400": {
                            "description": "You have a pending loan request",
                        },
                        "400": {
                            "description": "Validation error with request data",
                        },
                    }
                },
                "patch": {
                    "tags": ["RequestLoan"],
                    "summary": "Approve & Create Loan. Admin only",
                    "description": "Approves a loan request and creates the loan using request loan data",
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    },{
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "$ref": "#/definitions/ApproveRequestloan"
                        }
                    }],
                    "responses": {
                        "200": {
                            "description": "Loan Request Approved",
                        },
                        "404": {
                            "description": "Request Loan Not Found!",
                        },
                        "404": {
                            "description": "No Request loan with the given ID",
                        },
                        "400": {
                            "description": "Loan request not approved!",
                        },
                        "400": {
                            "description": "This loan request has already been approved",
                        },
                        "400": {
                            "description": "Validation error with request data",
                        },
                    }
                },
            },
            "/api/v1/loan": {
                "get": {
                    "tags": ["Loan"],
                    "summary": "Retrieves a list of Loans",
                    "description": "Retrieves a list of Loans in pagination of 5 loans per page",
                    "parameters": [{
                        "name": "Authorization",
                        "in": "header",
                        "required": True,
                        "type": "string",
                        "description": "Bearer <JWT>"
                    }],
                    "responses": {
                        "200": {
                            "description": "Loans retrieved!",
                        },
                        "404": {
                            "description": "No loans found for the given user ID",
                        },
                    }
                },
            },
            "/api/v1/loan/{loan_id}": {
                "get": {
                    "tags": ["Loan"],
                    "summary": "Retrieve Loan",
                    "description": "Retrieves a Loan",
                    "parameters": [{
                            "name": "loan_id",
                            "in": "path",
                            "required": True,
                            "type": "integer",
                            "format": "int64",
                            "description": "ID of the loan to retrieve"},{
                            "name": "Authorization",
                            "in": "header",
                            "required": True,
                            "type": "string",
                            "description": "Bearer <JWT>"}
                    ],
                    "responses": {
                        "200": {
                            "description": "Loan retrieved!",
                        },
                        "404": {
                            "description": "Loan not found or access denied.",
                        },
                    }
                },
            },
        },
        "definitions": {
            "UserRegister": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string", "example": "John Doe"},
                    "email": {"type": "string", "example": "john.doe@example.com"},
                    "password": {"type": "string", "example": "securepassword"},
                    "phone_number": {"type": "string", "example": "1234567890"}
                },
                "required": ["full_name", "email", "password"]
            },
            "UserLogin": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "john.doe@example.com"},
                    "password": {"type": "string", "example": "securepassword"}
                },
                "required": ["email", "password"]
            },
            "UserUpdate": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string", "example": "John Doe"},
                    "phone_number": {"type": "string", "example": "0987654321"}
                }
            },
            "Tokens": {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                    "refresh": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                }
            },
            "Token": {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                }
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "full_name": {"type": "string", "example": "John Doe"},
                    "email": {"type": "string", "example": "john.doe@example.com"},
                    "phone_number": {"type": "string", "example": "1234567890"}
                }
            },
            "Success": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "status": {"type": "integer", "example": 200},
                    "message": {"type": "string", "example": "Operation successful"}
                }
            },
            "Error": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "status": {"type": "integer", "example": 400},
                    "error": {"type": "string", "example": "Validation error"},
                    "message": {"type": "string", "example": "Invalid input data"}
                }
            },
            "Verification": {
                "type": "object",
                "properties": {
                    "address": {"type": "string", "example": "1 Wall Street"},
                    "is_verified": {"type": "boolean", "example": True},
                    "bvn": {"type": "string", "example": "39529153035"},
                    "date_verified": {"type": "string", "example": "07/03/2024 10:37:39"},
                    "user_id": {"type": "integer", "example": "1"}
                }
            },
            "Requestloan": {
                "type": "object",
                "properties": {
                    "amount": {"type": "integer", "example": 340943.094},
                    "amortization_type": {"type": "choice", "example": "daily, weekly, monthly, yearly"}
                }
            },
            "ApproveRequestloan": {
                "type": "object",
                "properties": {
                    "approval": {"type": "boolean", "example": True},
                }
            },
        }
    })
