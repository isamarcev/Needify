import "./messages";
import "@stdlib/deploy";
import "./job_offer";
import "./native_master";

message(0x050f) Deposit {
    query_id: Int as uint64;
    amount: Int as coins;
    destination: Address; // Job offer address
    response_destination: Address;
    forward_ton_amount: Int as coins;

}

message(0x051f) InternalDeposit {
    query_id: Int as uint64;
    amount: Int as coins;
    from: Address;
    response_destination: Address;
    forward_ton_amount: Int as coins;
}

message(0x052f) DepositNotification {
    query_id: Int as uint64;
    balance: Int as coins;
    response_destination: Address;
}

message(0x053f) WithdrawDeposit {
    query_id: Int as uint64;
    destination: Address;
    response_destination: Address;
}

struct NativeWalletData {
    balance: Int;
    owner: Address;
    master: Address;
    code: Cell;
}

@interface("org.ton.jetton.wallet")
contract NativeWallet with Deployable {
    balance: Int = 0;
    owner: Address;
    master: Address;
    const burning_percent: Int = 20000; // 20%

    init(owner: Address, master: Address) {
        self.owner = owner;
        self.master = master;
    }

    receive(msg: Deposit) {
        let ctx: Context = context();
        require(ctx.sender == self.owner, "Invalid sender");
        let final: Int = ctx.readForwardFee() * 2 + 
                            2 * gasConsumption + 
                                minTons + 
                                    msg.forward_ton_amount;   // Gas checks, forward_ton = 0.152
        require(ctx.value > final, "Invalid value"); 
        self.balance = self.balance - msg.amount; 
        require(self.balance >= 0, "Invalid balance");
        let init: StateInit = initOf NativeWallet(msg.destination, self.master);
        let to: Address = contractAddress(init);
        send(SendParameters {
            to: to,
            value: 0,
            mode: SendRemainingValue,
            bounce: false,
            body: InternalDeposit{
                query_id: msg.query_id,
                amount: msg.amount,
                from: self.owner,
                response_destination: msg.response_destination,
                forward_ton_amount: msg.forward_ton_amount
                }.toCell(),
            data: init.data,
            code: init.code
        });
    }

    receive(msg: WithdrawDeposit) {
        let ctx: Context = context();
        require(ctx.sender == self.owner, "Invalid sender");
        let d_init: StateInit = initOf NativeWallet(msg.destination, self.master);
        let fwd_amount: Int = myBalance() - ctx.readForwardFee() * 2 - gasConsumption - gasConsumption;
        let burning_amount: Int = self.balance * self.burning_percent / 100000;
        send(SendParameters{
            to: self.master,
            value: 0,
            mode: SendPayGasSeparately,
            body: BurnNotification {
                query_id: msg.query_id,
                amount: burning_amount,
                sender: self.owner,
                response_destination: msg.response_destination
            }.toCell()
        });
        let balance_to_send: Int = self.balance - burning_amount;
        self.balance = 0; 
        send(SendParameters {
            to: contractAddress(d_init),
            value: 0,
            mode: SendRemainingBalance,
            bounce: false,
            body: InternalTransfer{
                query_id: msg.query_id,
                amount: balance_to_send,
                from: self.owner,
                response_destination: msg.response_destination,
                forward_ton_amount: fwd_amount,
                forward_payload: beginCell().endCell().asSlice()}.toCell(),
            data: d_init.data,
            code: d_init.code
        });
    }


    receive(msg: Transfer) {
        let ctx: Context = context(); // Check sender
        require(ctx.sender == self.owner, "Invalid sender");

        let final: Int = ctx.readForwardFee() * 2 + 
                            2 * gasConsumption + 
                                minTons + 
                                    msg.forward_ton_amount;   // Gas checks, forward_ton = 0.152
        require(ctx.value > final, "Invalid value"); 
        // Update balance
        self.balance = self.balance - msg.amount; 
        require(self.balance >= 0, "Invalid balance");
        let init: StateInit = initOf NativeWallet(msg.destination, self.master);
        let to: Address = contractAddress(init);
        send(SendParameters {
            to: to,
            value: 0,
            mode: SendRemainingValue,
            bounce: false,
            body: InternalTransfer{
                query_id: msg.query_id,
                amount: msg.amount,
                from: self.owner,
                response_destination: msg.response_destination,
                forward_ton_amount: msg.forward_ton_amount,
                forward_payload: msg.forward_payload}.toCell(),
            data: init.data,
            code: init.code
        });
    }

    receive(msg: InternalDeposit) {
        let ctx: Context = context();
        let init: StateInit = initOf NativeWallet(msg.from, self.master);
        require(contractAddress(init) == ctx.sender, "Invalid sender");
        self.balance = self.balance + msg.amount;
        require(self.balance >= 0, "Invalid token amount");
        let msg_value: Int = self.msg_value(ctx.value);  
        let fwd_fee: Int = ctx.readForwardFee();
        if(msg.forward_ton_amount > 0) {
            msg_value = msg_value - msg.forward_ton_amount - fwd_fee;
            send(SendParameters {
                to: self.owner,
                value: msg.forward_ton_amount,
                mode: SendPayGasSeparately,
                bounce: false,
                body: DepositNotification {
                    query_id: msg.query_id,
                    balance: self.balance,
                    response_destination: msg.from,
                }.toCell()
            });
        }
        if (msg.response_destination != null && msg_value > 0) { 
            send(SendParameters {
                to: msg.response_destination, 
                value: msg_value,  
                bounce: false,
                body: Excesses{ query_id: msg.query_id }.toCell(),
                mode: SendPayGasSeparately
            });
        }
    }
    
    receive(msg: InternalTransfer) {
        let ctx: Context = context();
        if(ctx.sender != self.master) {
            let init: StateInit = initOf NativeWallet(msg.from, self.master);
            require(contractAddress(init) == ctx.sender, "Invalid sender");
        }
        self.balance = self.balance + msg.amount;
        require(self.balance >= 0, "Invalid token amount");
        let msg_value: Int = self.msg_value(ctx.value);  
        let fwd_fee: Int = ctx.readForwardFee();
        if(msg.forward_ton_amount > 0) {
            msg_value = msg_value - msg.forward_ton_amount - fwd_fee;
            send(SendParameters {
                to: self.owner,
                value: msg.forward_ton_amount,
                mode: SendPayGasSeparately,
                bounce: false,
                body: TransferNotification {
                    query_id: msg.query_id,
                    amount: msg.amount,
                    sender: msg.from,
                    forward_payload: msg.forward_payload
                }.toCell()
            });
        }
        if (msg.response_destination != null && msg_value > 0) { 
            send(SendParameters {
                to: msg.response_destination, 
                value: msg_value,  
                bounce: false,
                body: Excesses{ query_id: msg.query_id }.toCell(),
                mode: SendPayGasSeparately
            });
        }
    }

    receive(msg: Burn) {
        let ctx: Context = context();
        require(self.owner == ctx.sender, "Invalid sender");
        require(ctx.value > gasConsumption + gasConsumption + ctx.readForwardFee(), "Invalid ton amount");
        self.balance = self.balance - msg.amount;
        require(self.balance >= 0, "Invalid token amount");
        send(SendParameters{
            to: self.master,
            value: 0,
            mode: SendRemainingValue,
            body: BurnNotification {
                query_id: msg.query_id,
                amount: msg.amount,
                sender: self.owner,
                response_destination: msg.response_destination
            }.toCell()
        });
    }

    fun msg_value(value: Int): Int {
        let msg_value: Int = value;
        let ton_balance_before_msg: Int = myBalance() - msg_value;
        let storage_fee: Int = minTons - min(ton_balance_before_msg, minTons);
        msg_value = msg_value - (storage_fee + gasConsumption);
        return msg_value;
    }

    bounced(src: bounced<InternalTransfer>) {
        self.balance = self.balance + src.amount;
    }

    bounced(src: bounced<InternalDeposit>) {
        self.balance = self.balance + src.amount;
    }

    bounced(src: bounced<BurnNotification>) {
        self.balance = self.balance + src.amount;
    }

    get fun get_wallet_data(): NativeWalletData {
        return NativeWalletData{balance: self.balance, owner: self.owner, master: self.master, code: (initOf NativeWallet(self.owner, self.master)).code};
    }
}