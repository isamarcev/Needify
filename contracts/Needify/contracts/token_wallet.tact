import "./messages";
import "@stdlib/deploy";

const gasConsumption: Int = ton("0.02");
const minTons: Int = ton("0.02");

struct WalletData {
    balance: Int;
    owner: Address;
    master: Address;
    code: Cell;
}

@interface("org.ton.jetton.wallet")
contract TokenWallet with Deployable {
    balance: Int = 0;
    owner: Address;
    master: Address;

    init(owner: Address, master: Address) {
        self.owner = owner;
        self.master = master;
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
        let init: StateInit = initOf TokenWallet(msg.destination, self.master);
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
    
    receive(msg: InternalTransfer) {
        let ctx: Context = context();
        if(ctx.sender != self.master) {
            let init: StateInit = initOf TokenWallet(msg.from, self.master);
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

    bounced(src: bounced<BurnNotification>) {
        self.balance = self.balance + src.amount;
    }

    get fun get_wallet_data(): WalletData {
        return WalletData{balance: self.balance, owner: self.owner, master: self.master, code: (initOf TokenWallet(self.owner, self.master)).code};
    }
}