# Exceptions used by email providers (Mailgun, etc.)

class EmailTemporaryError(Exception): pass
class EmailPermanentError(Exception): pass