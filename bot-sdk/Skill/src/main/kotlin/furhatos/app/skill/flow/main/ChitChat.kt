package furhatos.app.skill.flow.main

import furhatos.app.skill.flow.Interaction
import furhatos.app.skill.info
import furhatos.app.skill.nlu.Fun
import furhatos.app.skill.nlu.ProvideName
import furhatos.flow.kotlin.*
import furhatos.gestures.Gestures
import furhatos.nlu.common.DontKnow
import furhatos.nlu.common.Maybe
import furhatos.nlu.common.No
import furhatos.nlu.common.Yes

val ChitChat: State = state {
    onEntry {
        furhat.say("Hey there! How's your day going?")
        furhat.listen()
    }

    onResponse<Fun> {
        when (it.text.toLowerCase()) {
            "good", "great", "awesome" -> furhat.say("Glad to hear that!")
            "not so good", "bad" -> furhat.say("I'm sorry to hear that. Anything I can do to cheer you up?")
            "tell me a joke" -> furhat.say("Sure! Why don't scientists trust atoms? Because they make up everything!")
            "what's your favorite color?" -> furhat.say("I don't have a favorite color, but I like all the colors of the rainbow!")
            else -> {
                furhat.say("That's interesting!")
                furhat.say("By the way, did you know that the average person spends about 6 months of their life waiting for red lights to turn green?")
            }
        }
        furhat.listen()
    }

    onNoResponse {
        furhat.say("${users.current.info.name}, I guess silence speaks volumes. And I know you ${
            if (users.current.info.likeRobot) "like robots" else "don't like robots"
        }")
        Gestures.BigSmile
    }

    onResponse<DontKnow> {
        furhat.say("No worries ${users.current.info.name}! Let's talk about something else.")
    }

    onResponse<Yes> {
        furhat.say("That's awesome ${users.current.info.name}! Do you have free time?")
    }

    onResponse<No> {
        furhat.say("No worries ${users.current.info.name}! Everyone has different preferences. Anything you'd like to talk about?")
        furhat.listen()
    }

    onResponse<Maybe> {
        furhat.say("${users.current.info.name}, I'm always up for an adventure! Is there anything specific on your mind? ${users.current.info.name}")
        furhat.listen()
    }
}