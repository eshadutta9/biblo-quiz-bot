package furhatos.app.skill.flow

import furhatos.app.skill.flow.main.Greeting
import furhatos.flow.kotlin.*
import furhatos.flow.kotlin.voice.PollyNeuralVoice
import furhatos.util.Gender
import furhatos.util.Language
// import org.apache.commons.io.Fi
import java.io.File
import java.sql.Timestamp

var MAXQUESTIONS = 8 // number of questions to the user (not including first 2)
var EMOTION = "neutral" // user emotion

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

val Interaction: State = state {
    onUserLeave(instant = true) {
        if (users.count > 0) {
            if (it == users.current) {
                furhat.attend(users.other)
                goto(Greeting)
            } else {
                furhat.glance(it)
            }
        } else {
            goto(Idle)
        }
    }

    onUserEnter(instant = true) {
        furhat.glance(it)
    }

}