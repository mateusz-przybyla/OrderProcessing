# Exceptions used by email providers (Mailgun, etc.)

class EmailTemporaryError(Exception): pass
class EmailPermanentError(Exception): pass

# Exceptions used by order processing tasks

class BusinessLogicError(Exception): pass
class TemporaryInfrastructureError(Exception): pass