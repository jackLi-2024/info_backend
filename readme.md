### 说明：
    1.框架运行
        本地运行: python3 lambda_function.py
        物理机部署: sh bin/start.sh
        aws-serverless运行: 入口为lambda_function.lambda_handler
    2.开发者需知
        开发者需要在resource新增自己python包
        例如实例中给出了test模块
            a.view  定义所有接口的地方
            b.utils  开发者自定义功能
            
            # 备注（重要）:开发者可以按文档全部调试自己的代码，也可以仅仅定义自己业务模块（例如test）,但是本机调试注意加上以下代码表示模块的查找路径
            `
            cur_dir = os.path.split(os.path.realpath(__file__))[0]
            sys.path.append("%s/" % cur_dir)
            `    
    3.备注
        开发者view中定义模型接口时，注意接口类必须继承BaseApi

##





            
            
    