package furhatos.app.skill.flow.main

import furhatos.flow.kotlin.State
import furhatos.app.skill.flow.Parent
import furhatos.flow.kotlin.*
import furhatos.gestures.Gestures
import furhatos.records.Location
val Explain: State =  state(Parent){
    onEntry {
        furhat.say {
            random {
                +"That was all I wanted to ask you. "
                +"That's all I had to say. "
            }
            +behavior { furhat.attend(users.other) }
            random{
                +"Have a nice day!"
                +"Have a lovely day! "
                +"I wish you a great rest of the day, "
            }
            +Gestures.Shake
        }
        furhat.attend(Location.DOWN)
    }
}