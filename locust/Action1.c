Action1()
{

	lr_start_transaction("get");

	web_reg_find("Text=xxx",
		LAST);

	web_custom_request("Head",
		"URL=http://10.0.244.108:7070/transaction_1", 
		"Method=GET",
		"Resource=0",
		"Referer=",
		LAST);

	lr_end_transaction("get", LR_AUTO);

	return 0;
}
