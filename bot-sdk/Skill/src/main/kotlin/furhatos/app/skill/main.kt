package furhatos.app.skill

import furhatos.app.skill.flow.Init
import furhatos.app.skill.flow.main.Idle
import furhatos.flow.kotlin.Flow
import furhatos.skills.Skill

class SkillSkill : Skill() {
    override fun start() {
        Flow().run(Init)
    }
}

fun main(args: Array<String>) {
    Skill.main(args)
}
