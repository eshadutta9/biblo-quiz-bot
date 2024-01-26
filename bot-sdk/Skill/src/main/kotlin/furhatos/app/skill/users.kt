package furhatos.app.skill

import furhatos.nlu.common.*
import furhatos.records.User

class UserInfo {
    var name: PersonName? = null
    var likeRobot: Boolean = false
    var level: Int = 0
    var correctIntRow: Int = 0
    var question: Int = 0
}

val User.info : UserInfo
    get() = data.getOrPut(UserInfo::class.qualifiedName, UserInfo())