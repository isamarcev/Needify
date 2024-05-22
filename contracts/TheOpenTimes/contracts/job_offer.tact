import "./token_wallet";
import "./messages";
import "@stdlib/ownable";
import "@stdlib/deploy";

const forwardTonAmount: Int = 1;
const notificationAmount: Int = 1;
const minTonStorage: Int = ton("0.3");
const minGasCunsumption: Int = ton("0.1");
const PlatformAddress: Address = address("EQBYuxKgz-W5DeoBTgxaLgxGO9OHOVgjt-1qV0HGoQtp9_Wt");


message(0x011f) Revoke {
    query_id: Int as uint32;
}

message(0x012f) Withdraw {
    to: Address;
    amount: Int;
}

message(0x013f) Approve {
    amount: Int as coins;
}

message(0x014f) GetJob {
    query_id: Int;
}

message(0x015f) CompleteJob {
    query_id: Int;
}

message(0x016f) ConfirmJob {
    query_id: Int;
}

message(0x017f) Appeal {
    query_id: Int;
    description: String;
}

message(0x018f) RevokeAppeal {
    query_id: Int;
}

message(0x019f) ConfirmAppeal {
    query_id: Int;
    verdict: Bool;
}

message(0x020f) BeJudge {
    query_id: Int;
}

message(0x021f) Vote {
    query_id: Int;
    verdict: Int as uint8;
}





struct ContractData {
    title: String;
    description: String;
    price: Int as coins;
    wallet_balance: Int as coins;
    owner: Address;
    doer: Address?;
    state: Int as uint8;
    jetton_master: Address;
    balance: Int as coins;
    my_jetton_address: Address;
    appeal_address: Address?;
}


contract AppealContract with Deployable {
    created_by: Address;
    JudgesAmount: Int = 0;
    const MaxJudges: Int = 1;
    judgesMap: map<Address, Int>;
    description: String;
    const NotVoted: Int = 3;
    const Positive: Int = 1;
    const Against: Int = 0;

    init(created_by: Address, description: String) {
        let ctx: Context = context();
        require(created_by == sender(), "Only for sender");
        require(ctx.value >= minTonStorage, "Not enough deposit. ");
        self.description = description;
        self.created_by = created_by;
        self.judgesMap = emptyMap();
    }

    receive(msg: BeJudge) {
        require(self.JudgesAmount < self.MaxJudges, "Only one judge could be added");
        require(self.judgesMap.get(sender()) != null, "Judge already added");
        self.judgesMap.set(sender(), self.NotVoted);
        self.JudgesAmount += 1;
    }

    receive(msg: Vote) {
        let ctx: Context = context();
        require(ctx.value >= minGasCunsumption, "Not enough value for gas. ");
        require(self.judgesMap.get(sender()) != null, "Only for judges");
        require(msg.verdict == self.Positive || msg.verdict == self.Against, "Invalid verdict");
        if (self.judgesMap.get(sender()) == self.NotVoted) {
            self.judgesMap.set(sender(), msg.verdict);
            self.verdict();
        }
    }

    fun verdict() {
        if (self.JudgesAmount < self.MaxJudges) {
            return;
        }
        let JM: map<Address, Int> = self.judgesMap;
        let positive: Int = 0;
        let against: Int = 0;
        let abstained: Int = 0;
        foreach (_, value in JM) {
            if (value == self.NotVoted) {
                abstained += 1;
            } else if (value) {
                positive += 1;
            } else {
                against += 1;
            }
        }
        require(abstained == 0, "Not all judges voted");
        let verdict: Bool = positive > against;
        send(SendParameters{
            to: self.created_by,
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero,
            body: ConfirmAppeal{
                query_id: now(),
                verdict: verdict
            }.toCell()});
        }

    receive(msg: Revoke) {
        require(self.created_by == sender(), "Only for creator");
        send(SendParameters{
            to: sender(),
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero,
            body: "Revoke appelation".asComment()
        });
    }

    receive(msg: ConfirmAppeal) {
        require(PlatformAddress == sender(), "Only for platform method");
        send(SendParameters{
            to: self.created_by,
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero,
            body: ConfirmAppeal{
                query_id: msg.query_id,
                verdict: msg.verdict
            }.toCell()
        });
    }
}


contract JobOffer with Deployable, Ownable {

    order: String;
    title: String;
    description: String;
    price: Int as coins;
    wallet_balance: Int as coins = 0;
    const feePercent: Int = ton("2");
    owner: Address;
    doer: Address?;
    state: Int;
    jetton_master: Address;
    const OfferCreated: Int = 0;
    const OfferPublished: Int = 1;
    const OfferAccepted: Int = 2;
    const OfferCompleted: Int = 3;
    const OfferConfirmed: Int = 4;
    const OfferAppelation: Int = 5;
    const OfferClosed: Int = 6;
    on_appelation_by: Address?;
    appeal_description: String?;
    appeal_address: Address?;


    init(title: String, description: String, price: Int, order: String, jetton_master: Address) {
        self.title = title;
        self.description = description;
        self.price = price;
        self.order = order;
        self.jetton_master = jetton_master;
        self.owner = sender();
        self.state = self.OfferCreated;
        let ctx: Context = context();

        send(SendParameters{
            to: sender(), // sending message back to the sender
            value: ctx.value - minTonStorage, // don't add Toncoins to the message...
            body: self.order.asComment(),
        }); 

        // Skip Reason: cskip_no_gas
        send(SendParameters{
            to: PlatformAddress, // sending message back to the sender
            value: 0, 
            body: self.order.asComment(),
            mode: SendPayGasSeparately
        });
    }

    receive(msg: Revoke) {
        self.requireOwner();
        require(self.state == self.OfferPublished || self.state == self.OfferCreated, "Not for current state");
        self.withdraw_deposit(self.owner, false);
    }

    receive(msg: Approve) {
        require(sender() == PlatformAddress, "Only for platform method");
        require(self.state == self.OfferCreated, "Invalid status for operation");
        self.wallet_balance = msg.amount;
        if (self.wallet_balance >= self.price) {
            self.state = self.OfferPublished;
            self.send_notification(self.owner, "Your task was published");
        } else {
            self.send_notification(self.owner, "Not enough deposit. Need to send more jettons");
        }
    }

    receive(msg: GetJob) {
        require(self.doer == null, "Job already got. ");
        require(sender() != self.owner, "Poster could not pick up job. ");
        require(self.state == self.OfferPublished, "Task is not approved. ");
        self.doer = sender();
        self.state = self.OfferAccepted;
    }

    receive(msg: CompleteJob) {
        require(self.doer == sender(), "Only doer can complete Job");
        require(self.state == self.OfferAccepted, "Only for accepted state.");
        self.state = self.OfferCompleted;
        self.send_notification(self.owner, "Completed job.");
    }

    receive(msg: ConfirmJob) {
        self.requireOwner();
        require(self.state == self.OfferCompleted || self.state == self.OfferAccepted, "Only for completed or accepted state.");
        self.state = self.OfferConfirmed;
        self.withdraw_deposit(self.doer!!, true);
    }
    receive(msg: Appeal) {
        require(self.on_appelation_by == null, "Only one appealation could be created");
        require(self.state == self.OfferAccepted || self.state == self.OfferCompleted, "Only for accepted or completed state.");
        require(self.doer == sender() || self.owner == sender(), "Only for doer or owner");
        let ctx: Context = context();
        require(ctx.value >= ton("0.65"), "Not enough deposit. ");
        let init: StateInit = initOf AppealContract(sender(), msg.description);
        let to: Address = contractAddress(init);
        self.appeal_address = to;
        send(SendParameters{
            to: to,
            value: 0,
            mode: SendRemainingValue,
            body: Deploy{
                queryId: 0,
            }.toCell(),
            data: init.data,
            code: init.code
        });
        self.on_appelation_by = sender();
        self.appeal_description = msg.description;
        self.state = self.OfferAppelation;
    }

    receive(msg: RevokeAppeal) {
        require(self.state == self.OfferAppelation, "Only for appealation state");
        require(self.on_appelation_by == sender(), "Only for appealation owner");
        let init: StateInit = initOf AppealContract(myAddress(), self.appeal_description!!);
        send(SendParameters{
            to: contractAddress(init),
            value: 0,
            mode: SendRemainingValue,
            body: Revoke{
                query_id: 0
                }.toCell()
        });
        self.on_appelation_by = null;
        self.appeal_description = null;
        self.state = self.OfferCompleted;
    }

    receive(msg: ConfirmAppeal) {
        require(self.state == self.OfferAppelation, "Only for appealation state");
        let init: StateInit = initOf AppealContract(myAddress(), self.appeal_description!!);
        require(sender() == contractAddress(init), "Only for appealation contract");
        self.state = self.OfferClosed;
        if (msg.verdict) {
            if (self.on_appelation_by == self.owner) {
                self.withdraw_deposit(self.owner, false);
            } else {
                self.withdraw_deposit(self.doer!!, true);
            }
        } else {
            if (self.on_appelation_by == self.owner) {
                self.withdraw_deposit(self.doer!!, true);
            } else {
                self.withdraw_deposit(self.owner, false);
            }
        }
    }

    fun withdraw_deposit(address: Address, withFee: Bool) {
        let ctx: Context = context();
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);  
        let to: Address = contractAddress(init);
        if (withFee) {
            send(SendParameters{
                to: to, 
                value: 0,
                mode: SendRemainingValue, 
                body: Transfer{ // 0x0f817ea5
                    query_id: 0,
                    amount: self.feePercent,
                    destination: PlatformAddress,
                    response_destination: address,
                    custom_payload: beginCell().endCell(),
                    forward_ton_amount: ton("0.1"),
                    forward_payload: beginCell().endCell().asSlice(),
                }.toCell(),
                data: init.data,
                code: init.code,
                });
            self.wallet_balance = self.wallet_balance - self.feePercent;
        }
        self.state = self.OfferClosed;
        send(SendParameters{
            to: to, 
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero, 
            body: Transfer{ // 0x0f817ea5
                query_id: 0,
                amount: self.wallet_balance,
                destination: address,
                response_destination: address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: ton("0.1"),
                forward_payload: beginCell().endCell().asSlice(),
            }.toCell(),
            data: init.data,
            code: init.code,
        });
    }

    get fun job_data(): ContractData {
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);
        let wallet_address: Address = contractAddress(init);
        return ContractData{
            title: self.title,
            description: self.description,
            price: self.price,
            wallet_balance: self.wallet_balance,
            owner: self.owner,
            doer: self.doer,
            state: self.state,
            jetton_master: self.jetton_master,
            balance: myBalance(),
            my_jetton_address: wallet_address,
            appeal_address: self.appeal_address
        };
    }

    fun send_notification(address: Address, message: String) {
        send(SendParameters{
                to: address,
                value: 1,
                mode: SendPayGasSeparately,
                body: message.asComment(),
        });
    }

    // only for testing purpose
    receive("restart") {
        send(SendParameters{
            to: sender(),
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero,
            body: "Restart".asComment()
        });
    }
}
