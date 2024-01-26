package furhatos.app.skill.nlu

import furhatos.nlu.*
import furhatos.nlu.common.PersonName
import furhatos.util.Language


class Fun: Intent(){
    override fun getExamples(lang: Language): List<String> {
        return listOf("That's funny?",
            "Haha",
            "Cool")
    }
}

class QAIntent(
    val question : String,
    val answer : String
) : SimpleIntent(listOf(question))

val Questions =
    listOf(
        QAIntent("how old are you", "I am five years old"),
        QAIntent("what is your name", "my name is Furhat"),
        QAIntent("what is your favorite food", "I love meatballs"))

class ProvideName(var name : PersonName? = null):Intent(){
    override fun getExamples(lang: Language): List<String> {
        return listOf("@name", "My @name is", "I am @name")
    }
}
