

class BaseUtils():  

	# is valid values
    TRUE = True;
    FALSE = False;

    # error code values
    # everything ok
    OK_CODE = "1";
    OK_MESSAGE = "";  

    @staticmethod
    def SetOKMessageDTO(dto):
        dto.IsValid = BaseUtils.TRUE
        dto.Code = BaseUtils.OK_CODE
        dto.Message = BaseUtils.OK_MESSAGE   