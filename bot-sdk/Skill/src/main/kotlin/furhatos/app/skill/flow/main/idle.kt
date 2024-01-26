package furhatos.app.skill.flow.main

import furhatos.flow.kotlin.*

val Idle: State = state {

    init {
        if (users.count > 0) {
            furhat.attend(users.random)
            goto(Greeting)
        }
    }


    onEntry {
        furhat.attendNobody()
    }

    onUserEnter {
        furhat.attend(it)
        goto(Greeting)
    }

}
