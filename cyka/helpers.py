def MemberDelete(member):
    member.priority_set.all().delete()
    member.assignment_set.all().delete()
    member.delete()

def ProjectDelete(project):
    for m in project.member_set.all():
        MemberDelete(m)
    project.topic_set.all().delete()
    project.delete()
