/*
delimiter //
CREATE TRIGGER msg_apn AFTER INSERT ON tig_ma_msgs
FOR EACH ROW
BEGIN
    SET cmd = CONCAT('python /var/lib/mysql/scripts/msg_apn.py ', NEW.msg)
    SET result = sys_exec(cmd);
END;
//
delimiter ;
*/

delimiter //
CREATE FUNCTION IF NOT EXISTS `jid_to_tig_id` (jabber_id VARCHAR(2049))
    RETURNS BIGINT(20) UNSIGNED
BEGIN
DECLARE tig_id BIGINT(20) UNSIGNED;
SELECT jid_id INTO tig_id FROM tig_ma_jids WHERE jid=jabber_id;
RETURN tig_id
END //
delimiter ;

delimiter //
CREATE PROCEDURE IF NOT EXISTS `get_messages`(
    IN sender VARCHAR(2049), IN receiver VARCHAR(2049), IN time TIMESTAMP)
BEGIN
    DECLARE sender_tig; 
    DECLARE receiver_tig; 
    SET sender_tig = jid_to_tig_id(sender);
    SET receiver_tig = jid_to_tig_id(receiver);
    SELECT msg FROM tig_ma_msgs
        WHERE ((owner_id=sender_tig AND buddy_id=receiver_tig)
                OR (owner_id=receiver_tig AND buddy_id=sender_tig))
            AND ts > time
        ORDER BY TIMESTAMP;
END //
delimiter ;
