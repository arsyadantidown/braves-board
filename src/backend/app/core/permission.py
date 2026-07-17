from app.models.board_member_model import BoardRole


PERMISSIONS = {
    "board.view": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "board.update": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "board.delete": {
        BoardRole.OWNER,
    },


    "member.view": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "member.invite": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "member.remove": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "member.change_role": {
        BoardRole.OWNER,
    },


    "column.view": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "column.create": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "column.rename": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "column.move": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "column.delete": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },

    "task.view": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "task.create": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "task.update": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
        BoardRole.MEMBER,
    },

    "task.delete": {
        BoardRole.OWNER,
        BoardRole.ADMIN,
    },
}


def has_permission(
    role: BoardRole,
    permission: str,
) -> bool:
    return role in PERMISSIONS.get(permission, set())