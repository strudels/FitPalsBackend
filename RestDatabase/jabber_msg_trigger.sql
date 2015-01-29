delimiter //
CREATE TRIGGER msg_apn AFTER INSERT ON tig_ma_msgs
FOR EACH ROW
BEGIN
    SET cmd = CONCAT('python /var/lib/mysql/scripts/msg_apn.py ', NEW.msg)
    SET result = sys_exec(cmd);
END;
//
delimiter ;
