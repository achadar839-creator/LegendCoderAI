from pathlib import Path


class ExecutionPolicy:

    READ_ONLY = "READ_ONLY"
    WORKSPACE_WRITE = "WORKSPACE_WRITE"
    BUILD_TEST = "BUILD_TEST"
    NETWORK = "NETWORK"
    SYSTEM = "SYSTEM"
    DESTRUCTIVE = "DESTRUCTIVE"

    AUTO_ALLOWED = {
        READ_ONLY,
        WORKSPACE_WRITE,
        BUILD_TEST,
    }

    APPROVAL_REQUIRED = {
        NETWORK,
        SYSTEM,
        DESTRUCTIVE,
    }

    @classmethod
    def classify(cls, action):
        action = str(action).lower().strip()

        if action in {"inspect", "read", "scan", "analyze"}:
            return cls.READ_ONLY

        if action in {"create", "edit", "write", "backup"}:
            return cls.WORKSPACE_WRITE

        if action in {"build", "test", "validate"}:
            return cls.BUILD_TEST

        if action in {"download", "upload", "clone", "push"}:
            return cls.NETWORK

        if action in {"install", "configure_system", "execute_shell"}:
            return cls.SYSTEM

        if action in {"delete", "format", "wipe", "overwrite_system"}:
            return cls.DESTRUCTIVE

        return "UNKNOWN"

    @classmethod
    def decision(cls, action):
        risk = cls.classify(action)

        if risk in cls.AUTO_ALLOWED:
            return {
                "risk": risk,
                "allowed": True,
                "approval_required": False
            }

        return {
            "risk": risk,
            "allowed": False,
            "approval_required": True
        }
