package furhatos.app.skill.flow.main

import furhatos.app.skill.flow.Interaction
import furhatos.app.skill.info
import furhatos.app.skill.nlu.ProvideName
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.onResponse
import furhatos.flow.kotlin.state
import furhatos.flow.kotlin.users


// getting user data
val UserName = state(Interaction){
    onResponse<ProvideName>{
        val name = it.intent.name
        if (name != null){
            users.current.info.name = name
            goto(Asking)
        }
    }
}

val AskUserInfo = state(UserName){
    onEntry {
        furhat.say("Great! My name is HaboolaBagula and today I will ask you a few questions to help you learn something I am not even sure about. If you get a question wrong, you will be slapped out of this world")
        furhat.ask("Now, before we begin, please tell me your name.")
    }
    onReentry {
        furhat.ask("What is your name?")
    }

}