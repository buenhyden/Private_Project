# -*- coding: utf-8 -*-
import pickle
import urllib3
import json
def OpenAPI():
    import pickle
    openapi = pickle.load(open('./etri_open_api_access_key', 'rb'))
    return openapi
def USE_ETRI_AI(analysisCode, text):
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"
    accessKey = OpenAPI().strip()
    requestJson = {
        'access_key' : accessKey,
        'argument' : {
            'text' : text,
            'analysis_code' : analysisCode
        }
    }
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )
    return str(response.data,'utf-8')
if __name__ == "__main__":
    text = """경구용 피임약은 여성호르몬을 강제로 조정해 배란을 억제하는 원리다. 호르몬 변화로 인해 신체에 다양한 증상이 함께 나타난다. 유방암과 우울증 위험을 높인다는 연구결과가 있는 반면, 류마티스 관절염 위험을 낮춘다는 연구결과도 있다.
최근에는 피임약 복용이 이성의 취향까지 바꾼다는 연구결과가 발표됐다. 이성을 선택할 때 선호하는 얼굴을 바꾼다는 내용의 연구다. 영국 스코틀랜드 스털링대학 연구진은 피임약을 복용하는 만18~24세 여성 18명과 복용하지 않는 37명을 대상으로 각각 2회에 걸쳐 취향을 조사했다.
조사에 사용된 얼굴은 컴퓨터 그래픽으로 남녀 20명의 사진을 합성해서 만들었다. 모니터에 매력적이라고 생각하는 얼굴이 나타나면 선택하도록 했다. 첫 번째 조사는 두 그룹 모두 피임약을 복용하지 않을 때 진행했다. 그 중에서도 임신 가능성이 가장 높은 배란 1~2일 전에 조사가 이뤄졌다. 두 번째 조사 역시 배란기에 해당하는 시기에 이뤄졌다. 다만, 한 그룹은 피임약을 복용하는 상태였다.
그 결과, 피임약을 복용하지 않은 그룹은 두 차례의 조사에서 모두 남성적인 얼굴에서 매력을 느끼는 것으로 조사됐다. 반면, 피임약을 복용한 그룹의 경우 복용 전에는 남성적인 얼굴에 매력을 느끼다가 복용 후에는 이 비율이 매우 낮아졌다.
    """
    print (USE_ETRI_AI('morp',text))
