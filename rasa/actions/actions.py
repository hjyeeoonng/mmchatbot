# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.events import SlotSet, ReminderScheduled, ReminderCancelled
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import datetime
# for diffusion
from diffuser.draw import Draw
from diffuser.inpaint import Inpaint
# for translation(Naver Papago API)
# import os
# import sys
import json
import urllib.request
#for translate
import deepl


# Naver Papago API
url = "https://openapi.naver.com/v1/papago/n2mt"
client_id = "x8zYugZhl75tuqxmWE2C" # 개발자센터에서 발급받은 Client ID 값
client_secret = "vdEzG4rLVA" # 개발자센터에서 발급받은 Client Secret 값


ALLOWED_DRAWING_OBJECTS = [
    "자화상", "집", "새", "고양이", "산과 나무", "꽃", "과일", "눈사람"
]
'''
ALLOWED_DRAWING_PROMPTS_CAT = [
    "black cat", "white cat", 
    "blue eyes", "yellow eyes", 
    "pearl necklace", "diamonds necklace"
]

ALLOWED_DRAWING_PROMPTS_FOREST = [
    "spring", "summer", "fall", "winter",
]

ALLOWED_INPAINTING_PROMPTS_CAT = [
    "wear a hat", "wear a diamond necklace",
]

ALLOWED_INPAINTING_PROMPTS_FOREST = [
    "sun in the sky", "clouds in the sky", "bluming flowers",
]
'''
# Allowed drawing_prompts
ALLOWED_DRAWING_PROMPTS_SELFPOTRRAIT = [
    "", "", "", "",
]

ALLOWED_DRAWING_PROMPTS_HOME = [
    "", "", "", "",
]

ALLOWED_DRAWING_PROMPTS_BIRD = [
    "", "", "", "",
]

ALLOWED_DRAWING_PROMPTS_CAT = [
    "검은 털", "흰 털", 
    "파란 눈", "노란 눈",
    "","",
    # "검은털 고양이", "흰털 고양이", "파란눈 고양이", "노란눈 고양이",
    # "진주 목걸이", "다이아몬드 목걸이",
]

ALLOWED_DRAWING_PROMPTS_FOREST = [
    "봄", "여름", "가을", "겨울",
]

ALLOWED_DRAWING_PROMPTS_FLOWER = [
    "", "", "", "",
]

ALLOWED_DRAWING_PROMPTS_FRUITS = [
    "사과", "배", "포도", "수박", "귤",
]

ALLOWED_DRAWING_PROMPTS_SNOWMAN = [
    "커다란 눈사람", "팔이 나뭇가지인 눈사람",
]


# Allowed inpainting_prompts
ALLOWED_INPAINTING_PROMPTS_SELFPOTRRAIT = [
    "", "", "", "",
]

ALLOWED_INPAINTING_PROMPTS_HOME = [
    "", "", "", "",
]

ALLOWED_INPAINTING_PROMPTS_BIRD = [
    "", "", "", "",
]

ALLOWED_INPAINTING_PROMPTS_CAT = [
    "모자를 쓴 고양이", "목걸이를 한 고양이",
]

ALLOWED_INPAINTING_PROMPTS_FOREST = [
    "하늘에 떠있는 해", "하늘에 있는 구름", "활짝 핀 꽃들",
]

ALLOWED_INPAINTING_PROMPTS_FLOWER = [
    "", "", "", "",
]

ALLOWED_INPAINTING_PROMPTS_FRUITS = [
    "접시 위에 있는", "", "", "",
]

ALLOWED_INPAINTING_PROMPTS_SNOWMAN = [
    "목도리를 한 눈사람", "모자를 쓴 눈사람",
]

#traslate_words for testing
translate_words = {
    "검은 털":"black fur",
    "까망 털":"black fur",
    "흰 털":"white fur",
    "하얀 털":"white fur",
    "파란 눈":"blue eyes",
    "노란 눈":"yellow eyes",
    "눈사람":"snowman",
    "모자":"hat",
    "모자를 쓴":"hatted",
    "모자를 쓴 고양이":"a cat in a hat",
    "커다란":"big",
}
print(translate_words['파란 눈'])

# Validate 'drawing_object' slot value
class ValidateObjectForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_object_form"

    def validate_drawing_object(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `drawing_object` value."""

        if slot_value not in ALLOWED_DRAWING_OBJECTS:
            dispatcher.utter_message(text=f"고양이/눈사람만 선택하실 수 있어요.")
            return {"drawing_object": None}
            
        dispatcher.utter_message(text=f"그림판에 {slot_value}를 그리고 '저장하기' 버튼을 눌러주세요!")

        dispatcher.utter_message(text="새로운 그림을 먼저 만들어보시겠어요? 아니면, 그리신 그림을 바로 꾸며보실래요?", buttons = [
            {
            "title" : "새로운 그림 먼저 만들래",
            "payload" : '/drawing'
            },
            {
            "title" : "그린 그림 꾸밀래",
            "payload" : '/inpainting'
            }
        ])

        return {"drawing_object": slot_value}


# Validate 'drawing_prompt' slot value
class ValidateDrawingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_drawing_form"

    def validate_drawing_prompt(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `drawing_prompt` value."""
        
        # 해결 방법: https://stackoverflow.com/questions/59199338/rasa-getting-slot-value-for-use-in-custom-action
        current_drawing_object_value = tracker.get_slot('drawing_object')
        if current_drawing_object_value == "고양이":
            ALLOWED_DRAWING_PROMPTS = ALLOWED_DRAWING_PROMPTS_CAT
        else:
            ALLOWED_DRAWING_PROMPTS = ALLOWED_DRAWING_PROMPTS_SNOWMAN
        
        # slot 이 list 인 경우
        for word in slot_value:
            if word.rstrip(',').strip(' ') not in ALLOWED_DRAWING_PROMPTS:
                msg = "죄송하지만 저는 그것을 그릴 수 없어요:("
                msg += f"제가 그릴 수 있는 {'/'.join(ALLOWED_DRAWING_PROMPTS)} 중에 선택해 정확히 입력해주세요."
                dispatcher.utter_message(msg)
                return {"drawing_prompt": None}
            
        # translation
        translated_drawing_prompt = []

        for word in slot_value:
            translated_drawing_prompt.append(translate_deepl(word.rstrip(',').strip(' ')))
            
        '''
        # slot 이 list 가 아닌 경우
        if slot_value not in ALLOWED_DRAWING_PROMPTS:
            msg = "죄송하지만 저는 그것을 그릴 수 없어요:("
            msg += f"제가 그릴 수 있는 {'/'.join(ALLOWED_DRAWING_PROMPTS)} 중에 선택해 정확히 입력해주세요."
            dispatcher.utter_message(msg)
            return {"drawing_prompt": None}

        # translation
        translated_drawing_prompt = translate(slot_value)
        '''

        print("--------- translated_drawing_prompt ---------")
        print(translated_drawing_prompt)

        return {"drawing_prompt": translated_drawing_prompt} # prompt 영어 번역본 저장 -> submit에서 영어로 보냄
                # {"drawing_prompt_kr": slot_value}] # prompt 한국어로 저장
    

# Validate 'inpainting_prompt' slot value
class ValidateInpaintingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_inpainting_form"

    def validate_inpainting_prompt(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `inpainting_prompt` value."""

        current_drawing_object_value = tracker.get_slot('drawing_object')
        if current_drawing_object_value == "고양이":
            ALLOWED_INPAINTING_PROMPTS = ALLOWED_INPAINTING_PROMPTS_CAT
        else:
            ALLOWED_INPAINTING_PROMPTS = ALLOWED_INPAINTING_PROMPTS_SNOWMAN

        # slot 이 list 인 경우
        for word in slot_value:
            if word.rstrip(',').strip(' ') not in ALLOWED_INPAINTING_PROMPTS:
                msg = "죄송하지만 저는 그것을 추가할 수 없어요:("
                msg += f"제가 추가할 수 있는 {'/'.join(ALLOWED_INPAINTING_PROMPTS)} 중에 선택해 정확히 입력해주세요."
                dispatcher.utter_message(msg)
                return {"inpainting_prompt": None}

        # translation
        translated_inpainting_prompt = []

        for word in slot_value:
            translated_inpainting_prompt.append(translate_deepl(word.rstrip(',').strip(' ')))


        '''
        # slot 이 list 가 아닌 경우
        if slot_value not in ALLOWED_INPAINTING_PROMPTS:
            msg = "죄송하지만 저는 그것을 추가할 수 없어요:("
            msg += f"제가 추가할 수 있는 {'/'.join(ALLOWED_INPAINTING_PROMPTS)} 중에 선택해 정확히 입력해주세요."
            dispatcher.utter_message(msg)
            return {"inpainting_prompt": None}

        # translation
        translated_inpainting_prompt = translate(slot_value)
        '''

        print("--------- translated_inpainting_prompt ---------")
        print(translated_inpainting_prompt)

        return {"inpainting_prompt": translated_inpainting_prompt} # prompt 영어 번역본 저장 -> submit에서 영어로 보냄
                # {"inpainting_prompt_kr": slot_value}] # prompt 한국어로 저장


# Submit Drawing Form to Diffuser
class SubmitDrawingForm(Action):
    def name(self) -> Text:
        return "submit_drawing_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Submit `drawing_form` value."""

        current_drawing_object_value = tracker.get_slot('drawing_object')
        current_drawing_prompt_value = tracker.get_slot('drawing_prompt')

        # slot 이 list 가 아닌 경우
        # current_drawing_prompt_value = "a black and white drawing of" + current_drawing_prompt_value + "on whiteboard"

        current_drawing_prompt_value.insert(0, "a black and white drawing of a " + translate(current_drawing_object_value))
        current_drawing_prompt_value.append("on whiteboard")
        diffusion = Draw(current_drawing_object_value, current_drawing_prompt_value)
        diffusion.draw_image()

        dispatcher.utter_message(text=f"그림을 완성했어요! '변경하기' 버튼을 눌러 확인해주세요.")
        # dispatcher.utter_message(text=f"특징을 더 추가해보실래요?")
        
        # button: https://forum.rasa.com/t/buttons-in-custom-actions/33969,
        #         https://github.com/RasaHQ/rasa/issues/11291,
        #         https://forum.rasa.com/t/button-payloads-and-predicting-actions/38579/2
        dispatcher.utter_message(text="특징을 더 추가해보시겠어요?", buttons = [
            {
            "title" : "응 추가할래",
            "payload" : '/inpainting'
            },
            {
            "title" : "아니",
            "payload" : '/deny'
            }
        ])
        
        return []


# Submit Inpainting Form to Diffuser
class SubmitInpaintingForm(Action):
    def name(self) -> Text:
        return "submit_inpainting_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Submit `inpainting_form` value."""

        current_inpainting_prompt_value = tracker.get_slot('inpainting_prompt')

        # slot 이 list 가 아닌 경우
        # current_inpainting_prompt_value = "a black and white drawing of" + current_inpainting_prompt_value + "on whiteboard"

        current_inpainting_prompt_value.insert(0, "a black and white drawing")
        current_inpainting_prompt_value.append("on whiteboard")
        diffusion = Inpaint(current_inpainting_prompt_value)
        diffusion.inpaint_image()

        dispatcher.utter_message(text=f"{tracker.get_slot('drawing_object')} 그림을 완성했어요!")
        dispatcher.utter_message(text=f"'변경하기' 버튼을 눌러 확인하실 수 있어요.")
        dispatcher.utter_message(text=f"마음에 드셨으면 좋겠네요:)")

        # 모든 slot value 초기화: https://forum.rasa.com/t/reset-slot-after-the-forms-complete/35355/2
        return [SlotSet("drawing_object", None), 
                SlotSet("drawing_prompt", None),
                SlotSet("inpainting_prompt", None)]
    

# Drawing Prompt Example Response to 'drawing_object' slot value
class ResponseToDrawingObjectPrompt(Action):
    def name(self) -> Text:
        return "response_drawing_prompt_example"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Response to `drawing_object` value."""

        dispatcher.utter_message(text=f"그리신 그림의 특징은 무엇인가요?")
        if tracker.get_slot('drawing_object') == "고양이":
            dispatcher.utter_message(text=f"{', '.join(ALLOWED_DRAWING_PROMPTS_CAT)} 과 같이 설명해주세요.")
        else:
            dispatcher.utter_message(text=f"{'/'.join(ALLOWED_DRAWING_PROMPTS_SNOWMAN)} 과 같이 설명해주세요.")
        dispatcher.utter_message(text=f"(다시 시작하고 싶다면 '다시 정하기'라고 말씀해주세요!)")

        return []


# Inpainting Example Response to 'drawing_object' slot value
class ResponseToDrawingObject(Action):
    def name(self) -> Text:
        return "response_inpainting_example"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Response to `drawing_object` value."""

        current_drawing_object_value = tracker.get_slot('drawing_object')
        if current_drawing_object_value == "고양이":
            dispatcher.utter_message(text=f"저는 고양이에 모자나 목걸이를 추가할 수 있어요.")
        else:
            dispatcher.utter_message(text=f"저는 눈사람에 모자나 목도리를 추가할 수 있어요.")
            # dispatcher.utter_message(text=f"저는 산과 나무에 해/구름/꽃을 추가할 수 있어요.")
        dispatcher.utter_message(text="추가하고 싶은 부분을 마스킹 색으로 칠하고 '저장하기' 버튼을 누른 후 '다 칠했어'라고 알려주세요.")

        return []
    

# Inpainting Prompt Example Response to 'drawing_object' slot value
class ResponseToDrawingObjectPrompt(Action):
    def name(self) -> Text:
        return "response_inpainting_prompt_example"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Response to `drawing_object` value."""

        dispatcher.utter_message(text=f"칠한 부분에 어떻게 추가하고 싶으세요?")

        current_drawing_object_value = tracker.get_slot('drawing_object')
        if current_drawing_object_value == "고양이":
            dispatcher.utter_message(text=f"{'/'.join(ALLOWED_INPAINTING_PROMPTS_CAT)} 와 같이 설명해주세요.")
        else:
            dispatcher.utter_message(text=f"{'/'.join(ALLOWED_INPAINTING_PROMPTS_SNOWMAN)} 과 같이 설명해주세요.")

        return []
    

# Submit Inpainting Form to Diffuser
class Finish(Action):
    def name(self) -> Text:
        return "action_finish"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Reset all slot's value."""

        return [SlotSet("drawing_object", None), 
                SlotSet("drawing_prompt", None),
                SlotSet("inpainting_prompt", None)]
    
'''
# https://rasa.com/docs/rasa/default-actions/
class ActionRestart(Action):

    def name(self) -> Text:
        return "action_restart"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # custom behavior

        return []
'''

# Translate Prompt with Naver Papago API
def translate(prompt):
    source = 'ko'
    target = 'en'

    encText = urllib.parse.quote(prompt)
    # data = "source=ko&target=en&text=" + encText
    data = f'source={source}&target={target}&text=' + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        decode = json.loads(response_body.decode('utf-8'))
        result = decode['message']['result']['translatedText']
        # print("--------- translation result ---------")
        # print(result)
    else:
        print("Error Code:" + rescode)

    return result.lower()

# Translate Prompt with Deepl API
def translate_deepl(prompt):
    auth_key = "3dd949ff-ce59-4359-be36-a85c086c887b:fx"
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(prompt, target_lang="EN-US")
    return result.text.lower()

# (추가) 사용자의 응답 없을 때
class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message("(답변을 안주시면 알림이 전송됩니다.)")

        date = datetime.datetime.now() + datetime.timedelta(seconds=20)
        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False,
        )

        return [reminder]


# (추가) 사용자의 응답 없을 때
class ActionReactToReminder(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # name = next(tracker.get_slot("PERSON"), "someone")
        dispatcher.utter_message(f"다 칠하셨나요?")

        return []
    

# (추가) 알림 취소 기능 (일정 시간 내에 사용자가 응답을 했을 때)
class ForgetReminders(Action):
    """Cancels all reminders."""

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(f"(알림을 취소합니다.)")

        # Cancel all reminders
        return [ReminderCancelled()]
    
    
# (추가) form slot 리셋 - 다시 그리기 기능  
class ResetFormAction(Action):
    def name(self):
        return "action_reset_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # dispatcher.utter_message(f"(form reset)")   ## 여기 사용자에게 띄울 말로 바꿔야 할듯
        # return [SlotSet(slot, None) for slot in tracker.slots.keys()]
        return [SlotSet("drawing_object", None), 
                SlotSet("drawing_prompt", None),
                SlotSet("inpainting_prompt", None)]
    



'''

class SubmitDrawing(Action):
    def name(self) -> Text:
        return "utter_submit_drawing"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Submit `drawing_form` value."""

        drawing_object = tracker.get_slot('drawing_object')
        drawing_prompt = tracker.get_slot('drawing_prompt')
        

        return [SlotSet("drawing_object", drawing_object), 
                SlotSet("drawing_prompt", drawing_prompt)]
    

class SubmitInpainting(Action):
    def name(self) -> Text:
        return "utter_submit_inpainting"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Submit `drawing_form` value."""

        inpainting_prompt = tracker.get_slot('inpainting_prompt')
        

        return [SlotSet("inpainting_prompt", inpainting_prompt)]

'''