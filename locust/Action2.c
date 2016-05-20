Action2()
{
	lr_start_transaction("post");

	web_reg_find("Text=yyy",
		LAST);
		
	web_custom_request("Head",
		"URL=http://10.0.244.108:7070/transaction_2", 
		"Method=POST",
		"Resource=0",
		"Referer=",
		"EncType=application/x-www-form-urlencoded; charset=utf-8",
		"Body=parm1=123&parm2=abc",
		LAST);

	lr_end_transaction("post", LR_AUTO);

	return 0;
}
