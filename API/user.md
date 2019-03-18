# User

## Activity(查看活动)

#### url
- /user/activity/

#### method
- GET


#### Return
```
{
    result_code: 1,
    activities: [{
        title: 活动名,
        start_time: 开始时间,
        end_time: 结束时间,
        content: 内容,
        pos: 地点
    },
    ...
    ]
}
```

## Bt Code

#### url
- /user/mycode/

#### method
- GET

#### doc
```
No doc found for this Api
```


## Bt Finish(维修完成)

#### url
- /user/finish/<int:rid>/

#### method
- GET


#### Args
|参数|内容|
|---|----|
|api_key|api_key|
|rid|订单编号|
|solved|true解决, false未解决(默认)|
#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功｜
|404|  |订单不存在|
|403|  |没有权限|
|-1|current status err|当前状态错误|


## Bt Order(接单)

#### url
- /user/order/<int:rid>/

#### method
- GET


### Param
rid: 订单表号
#### Return
```
{
    result_code: x,
    err_msg
}
```
##### Result_code
|result_code|err_msg|detail|
|-----|----|-----|
|1|success|成功|
|403| |没有权限|
|404| |订单不存在|
|-1|current status err|订单状态错误|

## Bt Ordered Reservation(查看已接订单)

#### url
- /user/myorder/

#### method
- GET


#### Return


## Bt Receive

#### url
- /user/receive/

#### method
- GET

#### doc
```
No doc found for this Api
```


## Bt Repair(改为维修中状态)

#### url
- /user/repair/<int:rid>/

#### method
- GET


#### Param
rid:订单编号
#### Return
```
{
    result_code:  x,
    err_msg: x
```
##### result_code
|result_code|err_msg|detail|
|----------|----|-------|
|1|success|成功|
|404| |订单不存在|
|403| |没有权限,非队员或非本人接单|
|-1|current status err|当前订单状态错误|

## Bt Summary(查看队员排名)

#### url
- /user/summary/

#### method
- GET


#### Return
```
{
    result_code: 1,
    data: [{
        name: 队员姓名,
        avg_score: 平均分,
        count: 接单量,
        score: 综合分
        },
        ...
    ]
}
```

## Bt Transfer

#### url
- /user/transfer/<int:id>/

#### method
- GET

#### doc
```
No doc found for this Api
```


## Bt Unorder Reservations(查看未接订单)

#### url
- /user/unorder/

#### method
- GET


#### Return
```
{
    result_code: 1,
    reservations: [{
        id: 订单编号,
        detail: 问题描述,
        create_time: 创建时间,
        user_info: {
            name: 姓名,
            sex: 性别,
            phone: 手机,
            qq: QQ号码
        }
    },
    ....]
}
```

## User Cancel Reservation(取消订单)

#### url
- /user/cancel/<int:rid>/

#### method
- GET


#### Arg:
    api_key: api_key


#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功|
|403| |用户不是订单所有者|
|401| |用户被禁用|
|-1|can not cancel|当前订单不可取消|

## User Confirm Reservation(确认订单)

#### url
- /user/confirm/<int:rid>/

#### method
- GET


#### Param
rid: 订单号
#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功取消|
|-1|can not confirm|订单状态错误,不能取消|

## User Evaluate Reservation(评价)

#### url
- /user/evaluate/<int:rid>/

#### method
- POST


#### Param
rid: 订单号
#### Data(json)
```
{
    "score": 分数(int),
    "evaluation: 评价(string)
}
```

#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|评价成功|
|-1|can not evaluate|订单状态错误,不能评价|

## User New Reservation(新订单)

#### url
- /user/reserve/

#### method
- POST


#### Arg:
    api_key: api_key
#### Data:
```
{
    detail: 问题描述,
    formid: 小程序formid
}
```
#### Return
```
{
    result_code: 状态码,
    err_msg: 错误信息
}
```
##### result_code
|code|err_msg|detail|
|--|---|---|
|1|success|成功|
|2|exist unfinished reservation|存在未完成订单|
|-1|invalid data|数据不合法|

## User Reservation(用户查看订单)

#### url
- /user/myreservation/

#### method
- GET


#### Return
```
{
    "result_code": 1,
    "evaluations": [
        {
            "create_time": "工单创建时间",
            "detail": "问题描述",
            "evaluation": "用户评价",
            "finish_time": "用户确认完成时间",
            "id": 工单号,
            "status": 工单状态,
            "score": 评分,
            "bt_info": null 或 {
                "name": "xxx",
                "phone": "xxx",
                "qq": "xxx",
                "sex": "male"/"female"
            }
        },
        .....
    ]
}
```

## User Reserve Code

#### url
- /user/reservecode/

#### method
- GET POST

#### doc
```
No doc found for this Api
```



