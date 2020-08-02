import time
import pygame
pygame.init()
pygame.font.init()


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

class Button: #base button class, not used on it's own but used for the useable buttons
    def __init__(self,text: pygame.Surface, text_anchor_x: int, text_anchor_y: int, active_bg: pygame.Surface, inactive_bg: pygame.Surface, x_pos: int, y_pos:int):
        self.is_active = False
        self.text = text
        self.active_bg = active_bg
        self.inactive_bg = inactive_bg
        self.text_offset_x = self.calcOffsetFromAnchorMode('x',text_anchor_x)
        self.text_offset_y = self.calcOffsetFromAnchorMode('y',text_anchor_y)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.active_bg.get_rect().move(self.x_pos,self.y_pos)

    def draw(self,surface: pygame.Surface) -> None:
        if self.is_active:
            image = self.active_bg
        else:
            image = self.inactive_bg

        surface.blit(image,(self.x_pos,self.y_pos))
        surface.blit(self.text, (self.x_pos+self.text_offset_x,self.y_pos+self.text_offset_y))
        #pygame.draw.rect(surface,(0,255,0),self.rect,2) #drawing outline of the rect used to dectect a click for debugging

    def isPosOverButton(self,pos:list) -> bool:
        return self.rect.collidepoint(pos)

    def changePos(self,new_x_pos = None,new_y_pos = None) -> None:
        x_change = 0
        y_change = 0
        if new_x_pos != None:
            if type(new_x_pos) is int:
                x_change = new_x_pos - self.x_pos
                self.x_pos = new_x_pos
            else:
                raise TypeError("pos arguments must be None or of type int")

        if new_y_pos != None:
            if type(new_y_pos) is int:
                y_change = new_y_pos - self.y_pos
                self.y_pos = new_y_pos
            else:
                raise TypeError("pos arguments must be None or one of the ButtonType's")
        self.rect = self.rect.move(x_change, y_change) #rect needs to reflect the new position

    def calcOffsetFromAnchorMode(self,axis: str ,anchor_type:int) -> int: 
        if anchor_type == Anchor.CENTER:
            if axis.lower() == "x":
                button_axis_length = self.active_bg.get_width()
                text_axis_length = self.text.get_width()
            elif axis.lower() == "y":
                button_axis_length = self.active_bg.get_height()
                text_axis_length = self.text.get_height()
            else:
                raise ValueError("axis argument must be either 'x' or 'y'")

            return int((button_axis_length - text_axis_length)/2)

        elif anchor_type in [Anchor.LEFT,Anchor.TOP]:
            return 0

        elif anchor_type == Anchor.RIGHT:
            return int(self.active_bg.get_width() - self.text.get_width())
        elif anchor_type == Anchor.BOTTOM:
            return int(self.active_bg.get_height() - self.text.get_height())

        else:
            raise ValueError("Anchor argument must be one of the Anchor types")



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
            self.prev_inactive_check = time.time()
            return self.on_click_action[0](*self.on_click_action[1])


class DoActionStayActiveOnclick(Button):
    def __init__(self, text, text_anchor_x, text_anchor_y, active_bg, inactive_bg, x_pos, y_pos,on_click_to_active_action,on_click_to_inactive_action):
        super().__init__(text, text_anchor_x, text_anchor_y, active_bg, inactive_bg, x_pos, y_pos)
        self.on_click_to_active_action = on_click_to_active_action
        self.on_click_to_inactive_action = on_click_to_inactive_action

    def click(self):
        self.is_active = not self.is_active
        if not self.is_active: #not to reflect the flipping prior to this if statement
            return self.on_click_to_inactive_action[0](*self.on_click_to_inactive_action[1])
        else:
            return self.on_click_to_active_action[0](*self.on_click_to_active_action[1])


class ShowChildrenOnClick(DoActionStayActiveOnclick):
    pass


class Slider:
    def __init__(self,slider_bg : pygame.Surface, slider_icon: pygame.Surface, slider_direction: int, x_pos: int, y_pos: int,min_value, max_value,return_format: str):
        self.is_active = False
        self.slider_bg = slider_bg
        self.slider_icon = slider_icon
        self.slider_direction = slider_direction #this is one of the direction constants
        self.x_pos = x_pos
        self.y_pos = y_pos
        #putting the cursor to the mininum starting value at the start
        if slider_direction in [Direction.LEFT_TO_RIGHT, Direction.TOP_TO_BOTTOM]:
            self.cursor_x_pos = x_pos
            self.cursor_y_pos = y_pos
            
        elif slider_direction == Direction.RIGHT_TO_LEFT:
            self.cursor_x_pos = x_pos + (slider_bg.get_width() - slider_icon.get_width())
            self.cursor_y_pos = y_pos
        elif slider_direction == Direction.BOTTOM_TO_TOP:
            self.cursor_x_pos = x_pos
            self.cursor_y_pos = y_pos + (slider_bg.get_height() - slider_icon.get_height())
        else:
            raise ValueError("slider_direction must be one of the Direction. constants")
        self.min_value = min_value
        self.max_value = max_value
        self.return_format = return_format

    def changeActiveState(self):
        self.is_active = not self.is_active

    def move_slider(self,pos,return_slider_value = False):
        if self.slider_direction in [Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT]: #icon movement locked to x-axis
            #see comments bellow for how this works
           cursor_pos = pos[0]
           if cursor_pos <= (max_cursor_pos := (self.slider_bg.get_width() - self.slider_icon.get_width() + self.x_pos)):
               if cursor_pos >= self.x_pos:
                   self.cursor_x_pos = cursor_pos
               else:
                    self.cursor_x_pos = self.x_pos
           else:
                self.cursor_x_pos = max_cursor_pos

        elif self.slider_direction in [Direction.TOP_TO_BOTTOM, Direction.BOTTOM_TO_TOP]: #icon movement locked to y-axis
            cursor_pos = pos[1]
            #checking the cursor is less than the max place the icon can go, placing it at the max it can position if too high
            if cursor_pos <= (max_cursor_pos := (self.slider_bg.get_height() - self.slider_icon.get_height() + self.y_pos)):
                if cursor_pos >= self.y_pos: #checking the cursor is a higher value than the top
                    self.cursor_y_pos = cursor_pos
                else:
                    self.cursor_y_pos = self.y_pos
            else:
                self.cursor_y_pos = max_cursor_pos
                
        if return_slider_value:
            return self.get_current_value()

    def get_current_value(self):
        # min value + (gap between max and min)/percent along the slider the icon is
        #the 1 - percent along the slider inverts it for when the slider is the opposite way round
        if self.slider_direction == Direction.LEFT_TO_RIGHT:
            return_value = self.min_value + (self.max_value - self.min_value) * (self.cursor_x_pos - self.x_pos)/(self.slider_bg.get_width()- self.slider_icon.get_width())
        elif self.slider_direction == Direction.RIGHT_TO_LEFT:
            return_value = self.min_value + (self.max_value - self.min_value) * (1 - (self.cursor_x_pos - self.x_pos)/(self.slider_bg.get_width()- self.slider_icon.get_width()))
        elif self.slider_direction == Direction.TOP_TO_BOTTOM:
            return_value = self.min_value + (self.max_value - self.min_value) * (self.cursor_y_pos - self.y_pos)/(self.slider_bg.get_height()- self.slider_icon.get_height())
        elif self.slider_direction == Direction.BOTTOM_TO_TOP:
            return_value = self.min_value + (self.max_value - self.min_value) * (1 - (self.cursor_y_pos - self.y_pos)/(self.slider_bg.get_height()- self.slider_icon.get_height()))
        return self.return_format.format(return_value)

    def isPosOverSliderIcon(self,pos):
        #TODO: Make same change here as I did to the button
        return self.slider_icon.get_rect().move(self.cursor_x_pos,self.cursor_y_pos).collidepoint(pos)

    def draw(self,surface):
        surface.blit(self.slider_bg,(self.x_pos,self.y_pos))
        surface.blit(self.slider_icon,(self.cursor_x_pos,self.cursor_y_pos))


class Anchor:
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4


class Direction:
    TOP_TO_BOTTOM = 0
    BOTTOM_TO_TOP = 1
    LEFT_TO_RIGHT = 2
    RIGHT_TO_LEFT = 3

