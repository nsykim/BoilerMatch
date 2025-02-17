from enum import Enum

class Preference(Enum):
    NOT_SPECIFIED = 0
    NEVER = 1
    RARELY = 2
    DONT_CARE = 3 
    SOMETIMES = 4
    OFTEN = 5

# Enum for user specified weights/dealbreakers
class IsDealbreaker(Enum):
    NOT_DEALBREAKER = False #DEFAULT
    DEALBEAKER = True

user_info = {
    "display_name" : name,
    "college" : college,
    "prompts" : prompts_list, #3 prompts
    "images" : images,
}

# here's a list of preferences. 
# each person will pick a number from the enum for each preferencce
# there will also be a boolean dealbreaker that will be stored
preferences = {
    "Cleanliness",
    "Alcohol",
    "Marijuana",
    "Smoking",
    "Exercise",
    "Sleep Schedule"

}

# here's a list of prompts. 
# each person will pick 3 prompts from this list
# and store the prompt index and their response in the prompts section of user info
prompt_list = { 
    "",
    "",
    "",
    "",
}


# images = { #store 3 images. Will be jpg links stored somewhere else
#     "" * 3
# }