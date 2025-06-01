CREATE PROCEDURE dbo.SendTelegramMessage
    @Message NVARCHAR(MAX) = 'test',
    @BotToken NVARCHAR(100) = 'SMTH:SMTH', 
    @ChannelID NVARCHAR(100) = '' --to be obtained by the bot
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @URL NVARCHAR(MAX)
    DECLARE @ResponseText NVARCHAR(MAX)
    DECLARE @Object INT
    DECLARE @HTTPStatus INT
    DECLARE @ErrorMessage NVARCHAR(MAX)
    
    -- Construct the Telegram API URL
    SET @URL = 'https://api.telegram.org/bot' + @BotToken + '/sendMessage'
    
    -- Create the HTTP object
    EXEC sp_OACreate 'MSXML2.XMLHTTP', @Object OUT
    IF @Object IS NULL
    BEGIN
        RAISERROR('Failed to create HTTP object', 16, 1)
        RETURN
    END
    
    BEGIN TRY
        -- Open the connection
        EXEC sp_OAMethod @Object, 'open', NULL, 'POST', @URL, 'false'
        
        -- Set the content type
        EXEC sp_OAMethod @Object, 'setRequestHeader', NULL, 'Content-Type', 'application/json'
        
        -- Prepare the message body
        DECLARE @RequestBody NVARCHAR(MAX)
        SET @RequestBody = '{"chat_id":"' + @ChannelID + '","text":"' + REPLACE(@Message, '"', '\"') + '","parse_mode":"HTML"}'
        
        -- Send the request
        EXEC sp_OAMethod @Object, 'send', NULL, @RequestBody
        
        -- Get the response
        EXEC sp_OAMethod @Object, 'status', @HTTPStatus OUT
        
        IF @HTTPStatus <> 200
        BEGIN
            EXEC sp_OAMethod @Object, 'responseText', @ResponseText OUT
            SET @ErrorMessage = 'HTTP Error: ' + CAST(@HTTPStatus AS NVARCHAR(10)) + ' - ' + @ResponseText
            RAISERROR(@ErrorMessage, 16, 1)
        END
    END TRY
    BEGIN CATCH
        SET @ErrorMessage = ERROR_MESSAGE()
        RAISERROR(@ErrorMessage, 16, 1)
    END CATCH
    
    -- Clean up
    EXEC sp_OADestroy @Object
END
GO 