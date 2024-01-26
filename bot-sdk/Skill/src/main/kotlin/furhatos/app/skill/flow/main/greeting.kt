package furhatos.app.skill.flow.main

import furhatos.app.skill.flow.Parent
import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.onResponse
import furhatos.flow.kotlin.state
import furhatos.gestures.Gestures
import furhatos.nlu.common.*
import furhatos.app.skill.nlu.Questions

val Greeting: State = state(Parent) {
    onEntry {
        /** Greet the user **/
        furhat.say {
            random {
                +"Hello good to see you"
                +"What's hanging dawg?"
                +"Yo my man, what up"
            }
            +Gestures.BigSmile
        }

        furhat.listen()
    }

    onResponse<Greeting> {
        val canIAskYouSomething = furhat.askYN("Can I ask you something?")
        if (canIAskYouSomething) {
            goto(AskUserInfo)
        } else {
            furhat.say("Sorry to bother you. ")
            furhat.gesture(Gestures.Thoughtful)
            furhat.stopGestures()
            goto(Explain)
        }
    }

    onResponse(Questions) {
        furhat.say("You said:" + it.text)
    }

    onResponse<Yes> {
        furhat.say("Hello World! ")
        furhat.listen()
    }

    onResponse<No> {
        furhat.say("Ok.")
    }

    onResponse<Maybe> {
        furhat.say("Okay Ill try, Hello world, haha")
    }

    onResponse<Goodbye> {
        furhat.say("Okay bye! See ya later, alligator")
    }

}

