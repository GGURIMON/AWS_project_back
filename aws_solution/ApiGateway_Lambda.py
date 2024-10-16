from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway

class FastApiCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # LMM.py를 위한 Lambda 함수
        lmm_lambda = _lambda.Function(
            self, "LMMLambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="LMM.handler",  # LMM.py의 Mangum 핸들러
            code=_lambda.Code.from_asset("path/to/your/lmm")  # LMM.py가 있는 경로
        )

        # main.py를 위한 Lambda 함수
        main_lambda = _lambda.Function(
            self, "MainLambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="main.handler",  # main.py의 Mangum 핸들러
            code=_lambda.Code.from_asset("path/to/your/main")  # main.py가 있는 경로
        )

        # RestApi 생성 및 각 Lambda와 연결
        api = apigateway.RestApi(self, "FastAPIGateway")

        # LMM 경로 추가
        lmm_integration = apigateway.LambdaIntegration(lmm_lambda)
        api.root.add_resource("lmm").add_method("GET", lmm_integration)

        # Main 경로 추가
        main_integration = apigateway.LambdaIntegration(main_lambda)
        api.root.add_resource("main").add_method("GET", main_integration)
