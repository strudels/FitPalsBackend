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
    SET sender_tig = jid_to_tig_id(sender);
*/

DROP FUNCTION IF EXISTS `jid_to_tig_id`;
delimiter //
CREATE FUNCTION `jid_to_tig_id` (jabber_id VARCHAR(2049))
    RETURNS BIGINT(20) UNSIGNED
BEGIN
    DECLARE tig_id BIGINT(20) UNSIGNED;
    SELECT jid_id INTO tig_id FROM tig_ma_jids WHERE jid=jabber_id;
    RETURN tig_id;
END //
delimiter ;

DROP PROCEDURE IF EXISTS `get_messages`;
delimiter //
CREATE PROCEDURE `get_messages`(
    IN sender VARCHAR(2049), IN receiver VARCHAR(2049))
BEGIN
    DECLARE sender_tig BIGINT(20) UNSIGNED; 
    DECLARE receiver_tig BIGINT(20) UNSIGNED; 
    SET sender_tig = jid_to_tig_id(sender);
    SET receiver_tig = jid_to_tig_id(receiver);
    SELECT msg FROM tig_ma_msgs
        WHERE owner_id=sender_tig AND buddy_id=receiver_tig
        ORDER BY ts;
END //
delimiter ;

DROP PROCEDURE IF EXISTS `delete_messages`;
delimiter //
CREATE PROCEDURE `delete_messages`(
    IN sender VARCHAR(2049), IN receiver VARCHAR(2049))
BEGIN
    DECLARE sender_tig BIGINT(20) UNSIGNED; 
    DECLARE receiver_tig BIGINT(20) UNSIGNED; 
    SET sender_tig = jid_to_tig_id(sender);
    SET receiver_tig = jid_to_tig_id(receiver);
    DELETE FROM tig_ma_msgs
        WHERE owner_id=sender_tig AND buddy_id=receiver_tig;
END //
delimiter ;
