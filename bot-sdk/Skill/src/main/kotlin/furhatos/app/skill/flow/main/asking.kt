package furhatos.app.skill.flow.main

import furhatos.app.skill.info
import furhatos.flow.kotlin.State
import furhatos.flow.kotlin.*
import furhatos.nlu.common.DontKnow
import furhatos.nlu.common.Maybe
import furhatos.nlu.common.No
import furhatos.nlu.common.Yes

val Asking:State = state(){
    onEntry {
        furhat.ask{
            +"Do you like robots, ${users.current.info.name}?"
        }
        furhat.listen()
    }
    onResponse<Yes> {
        users.current.info.likeRobot = true
        furhat.say("How Nice")
        goto(ChitChat)

    }
    onResponse<No> {
        furhat.say("Aww that's a shame")
        goto(ChitChat)
    }

    onResponse<DontKnow> {
        furhat.say("Hmm That's Okay")
    }

    onResponse<Maybe> {
        furhat.say("I'm Going to tell you about it.")
    }

}