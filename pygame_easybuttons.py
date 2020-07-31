import time
import pygame
pygame.init()
pygame.font.init()


def createButton(button_type, *args):
        existing_button_types = [DoActionOnClick,DoActionStayActiveOnclick]
        if button_type in existing_button_types:
            return button_type(*args)
        else:
            raise ValueError("button_type argument must be one of the button types")

#when a button needs to have it's state set to inactive after a certain time period it's added to a list called buttonsToHandleActiveCountdownOn
buttonsToHandleActiveCountdownOn = []
#these two functions handle counting down and then setting the button to inactive after a time has elapsed
def handleButtonActiveCountdown_timed() -> None:#this one uses a time in seconds for unlocked frame rates
    global buttonsToHandleActiveCountdownOn
    nowtime = time.time()
    for button in buttonsToHandleActiveCountdownOn:
        button.until_inactive -= (nowtime - button.prev_inactive_check)
        button.prev_inactive_check = nowtime
        if button.until_inactive <= 0:
            button.is_active = False
            button.until_inactive = button.until_inactive_original # resets this back to the original time 
            buttonsToHandleActiveCountdownOn.remove(button)

def handleButtonActiveCountdown_frames() -> None: #this one does it on frames for games on locked frames
    global buttonsToHandleActiveCountdownOn
    for button in buttonsToHandleActiveCountdownOn:
        button.until_inactive -= 1
        if button.until_inactive == 0:
            button.is_active = False
            button.until_inactive = button.until_inactive_original # resets this back to the original time 
            buttonsToHandleActiveCountdownOn.remove(button)

class Button:
    def __init__(self,text: pygame.Surface, text_anchor_x: int, text_anchor_y: int, active_bg: pygame.Surface, inactive_bg: pygame.Surface, x_pos: int, y_pos:int):
        self.is_active = False
        self.text = text
        self.active_bg = active_bg
        self.inactive_bg = inactive_bg
        self.text_offset_x = self.setOffsetFromAnchorMode('x',text_anchor_x)
        self.text_offset_y = self.setOffsetFromAnchorMode('y',text_anchor_y)
        self.x_pos = x_pos
        self.y_pos = y_pos

    def draw(self,surface: pygame.Surface) -> None:
        if self.is_active:
            image = self.active_bg
        else:
            image = self.inactive_bg

        surface.blit(image,(self.x_pos,self.y_pos))
        surface.blit(self.text, (self.x_pos+self.text_offset_x,self.y_pos+self.text_offset_y))

    def isPosOverButton(self,pos:list) -> bool:
        return self.active_bg.get_rect().move(self.x_pos,self.y_pos).collidepoint(pos)

    def changePos(self,new_x_pos = None,new_y_pos = None):
        if new_x_pos != None:
            if type(new_x_pos) is int:
                self.x_pos = new_x_pos
            else:
                raise TypeError("pos arguments must be None or of type int")

        if new_y_pos != None:
            if type(new_y_pos) is int:
                self.y_pos = new_y_pos
            else:
                raise TypeError("pos arguments must be None or of type int")

    def setOffsetFromAnchorMode(self,axis: str ,anchor_type:int) -> None:
        if anchor_type == anchor.CENTER:
            if axis.lower() == "x":
                button_axis_length = self.active_bg.get_width()
                text_axis_length = self.text.get_width()
            elif axis.lower() == "y":
                button_axis_length = self.active_bg.get_height()
                text_axis_length = self.text.get_height()
            else:
                raise ValueError("axis argument must be either 'x' or 'y'")

            return int((button_axis_length - text_axis_length)/2)

        elif anchor_type in [anchor.LEFT,anchor.TOP]:
            return 0

        elif anchor_type == anchor.RIGHT:
            return int(self.active_bg.get_width() - self.text.get_width())
        elif anchor_type == anchor.BOTTOM:
            return int(self.active_bg.get_height() - self.text.get_height())
        
        else:
            raise ValueError("Anchor argument must be one of the anchor types")



class DoActionOnClick(Button):
    def __init__(self, text: pygame.Surface, text_anchor_x: int, text_anchor_y: int, active_bg: pygame.Surface, inactive_bg: pygame.Surface ,x_pos: int,y_pos: int,
                 on_click_action: list ,until_inactive: float):
        super().__init__(text, text_anchor_x, text_anchor_y, active_bg, inactive_bg,x_pos,y_pos)
        self.on_click_action = on_click_action
        #this is used by the handle animation function to make the button unclicked
        self.until_inactive_original = until_inactive #this one isn't changed so the line below can be reset when it reaches 0
        self.until_inactive = until_inactive
        self.prev_inactive_check = time.time() #this is only used for when the countdown is done on a timer

    def click(self):
        if not self.is_active:
            self.is_active = True
            buttonsToHandleActiveCountdownOn.append(self)
            return self.on_click_action[0](*self.on_click_action[1])

class DoActionStayActiveOnclick(Button):
    def __init__(self, text, text_anchor_x, text_anchor_y, active_bg, inactive_bg, x_pos, y_pos,on_click_to_active_action,on_click_to_inactive_action):
        super().__init__(text, text_anchor_x, text_anchor_y, active_bg, inactive_bg, x_pos, y_pos)
        self.on_click_to_active_action = on_click_to_active_action
        self.on_click_to_inactive_action = on_click_to_inactive_action

    def click(self):
        if self.is_active:
            self.is_active = False
            return self.on_click_to_inactive_action[0](*self.on_click_to_inactive_action[1])
        else:
            self.is_active = True
            return self.on_click_to_active_action[0](*self.on_click_to_active_action[1])

class ButtonType:
    SHOW_CHILDREN_ONCLICK = 0
    STAY_ACTIVE_ONCLICK = DoActionStayActiveOnclick
    DONT_STAY_ACTIVE_ONCLICK = DoActionOnClick

class anchor:
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4

"""
writing documentation
"""