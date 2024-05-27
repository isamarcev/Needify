import "./messages";
import "@stdlib/ownable";
import "@stdlib/deploy";

const forwardTonAmount: Int = 1;
const notificationAmount: Int = 1;
const minTonStorage: Int = ton("0.3");
const minGasCunsumption: Int = ton("0.1");
const simple_message_request: Int = ton("0.05");

const PlatformAddress: Address = address("EQBYuxKgz-W5DeoBTgxaLgxGO9OHOVgjt-1qV0HGoQtp9_Wt");
const jetton_transer_value: Int = ton("0.06");


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
    mark: Int? as uint8;
    review: String?;
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

message(0x022f) ChooseDoer {
    doer: Address;
}


message(0x023f) CheckPublish {
    query_id: Int as uint64;
}

message(0x053f) WithdrawDeposit {
    query_id: Int as uint64;
    destination: Address;
    response_destination: Address;
}




struct ContractData {
    title: String;
    description: String;
    price: Int as coins;
    owner: Address;
    doer: Address?;
    state: Int as uint8;
    balance: Int as coins;
    jetton_wallet: Address?;
    native_wallet: Address?;
    jetton_balance: Int as coins;
    wallet_balance: Int as coins;
    appeal_address: Address?;
    mark: Int?;
    review: String?;
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
            body: null
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
    owner: Address;
    doer: Address? = null;
    state: Int;

    on_appelation_by: Address?;
    appeal_description: String?;
    appeal_address: Address?;

    jetton_master: Address;
    jetton_wallet: Address? = null;
    jetton_balance: Int as coins = 0;
    
    native_master: Address;
    native_wallet: Address? = null;
    wallet_balance: Int as coins = 0;
    const native_public_cost: Int = ton("100");

    costs: map<Address, Int>;

    const PublicCost: Int = ton("100");
    const feePercent: Int = 2000; // 2 %

    const OfferCreated: Int = 0;
    const OfferPrePublished: Int = 7;
    const OfferPublished: Int = 1;
    doers: map<Address, Bool>;
    const maxVacancies: Int = 2;
    const OfferAccepted: Int = 2;
    const OfferCompleted: Int = 3;
    const OfferConfirmed: Int = 4;
    const OfferAppelation: Int = 5;
    const OfferClosed: Int = 6;
    mark: Int? = null;
    review: String? = null;

    init(title: String, description: String, price: Int, order: String, jetton_master: Address, native_master: Address) {
        let ctx: Context = context();
        require(ctx.value >= (minTonStorage + (simple_message_request * 3)), "Not enough deposit. ");
        self.title = title;
        self.description = description;
        self.price = price;
        self.order = order;
        self.jetton_master = jetton_master;
        self.native_master = native_master;
        self.owner = ctx.sender;
        self.state = self.OfferCreated;
        let remaining_value: Int = ctx.value - minTonStorage;
        send(SendParameters{
            to: self.jetton_master, // sending message back to the sender
            value: simple_message_request, 
            body: ProvideWalletAddress{
                query_id: 0,
                owner_address: myAddress(),
                include_address: false,
            }.toCell(),
        });
        
        send(SendParameters{
            to: self.native_master, // sending message back to the sender
            value: simple_message_request, 
            body: ProvideWalletAddress{
                query_id: 0,
                owner_address: myAddress(),
                include_address: false,
            }.toCell(),
        });
        send(SendParameters{
            to: PlatformAddress, // sending message back to the sender
            value: 1, 
            body: "Order was deployed. ".asComment(),
            mode: SendPayGasSeparately
        });
    }

    receive(msg: TakeWalletAddress) {
        let ctx: Context = context();
        if (ctx.sender == self.jetton_master) {
            self.jetton_wallet = msg.wallet_address;
        } else if (ctx.sender == self.native_master) {
            self.native_wallet = msg.wallet_address;
        }
        self.tryPublish();
    }

    receive(msg: CheckPublish) {
        let ctx: Context = context();
        require(ctx.sender == myAddress(), "Only for order contract method");
        if (self.state == self.OfferCreated || self.state == self.OfferPrePublished) {
            if (self.costs.get(self.jetton_wallet!!) != null) {
                self.jetton_balance = self.costs.get(self.jetton_wallet!!)!!;
                self.costs.del(self.jetton_wallet!!);
            }
            if (self.costs.get(self.native_wallet!!) != null) {
                self.wallet_balance = self.costs.get(self.native_wallet!!)!!;
                self.costs.del(self.native_wallet!!);
            }
        }
        if (!self.tryPublish() && myBalance() > ton("0.1")) {
            send(SendParameters{
                to: myAddress(), 
                value: simple_message_request, 
                body: CheckPublish{
                    query_id: 0
                }.toCell(),
            });
        }
    }

    receive(msg: TransferNotification) {
        let ctx: Context = context();
        if (self.costs.get(ctx.sender) == null) {
            self.costs.set(ctx.sender, msg.amount);
        } else {
            let updated_value: Int = self.costs.get(ctx.sender)!! + msg.amount;
            self.costs.set(ctx.sender, updated_value);
        }
        if (self.state == self.OfferPrePublished || self.state == self.OfferCreated) {
            send(SendParameters{
            to: myAddress(), 
            value: simple_message_request, 
            body: CheckPublish{
                query_id: 0
            }.toCell(),
        });
        }
    }

    fun tryPublish(): Bool {
        require(self.state == self.OfferCreated || self.state == self.OfferPrePublished, "Invalid status for operation");
        if (self.jetton_balance >= self.price && self.wallet_balance >= self.PublicCost) {
            self.state = self.OfferPublished;
            return true;
        } else {
            self.state = self.OfferPrePublished;
            return false;
        }
    }

    receive(msg: Revoke) {
        self.requireOwner();
        require(self.state == self.OfferPublished || self.state == self.OfferCreated || self.state == self.OfferPrePublished, "Not for current state");
        self.withdraw_deposit(self.owner, false);
    }

    receive(msg: GetJob) {
        let ctx: Context = context();
        require(ctx.value >= minGasCunsumption, "Not enough value for gas. ");
        require(self.doer == null, "Job already got. ");
        require(sender() != self.owner, "Poster could not pick up job. ");
        require(self.state == self.OfferPublished, "Task is not approved. ");
        let map_size: Int = 0;
        let map_: map<Address, Bool> = self.doers;
        foreach (doer, _ in map_) {
            map_size += 1;
        }
        require(map_size <= self.maxVacancies, "No more vacancies. ");
        if (self.doers.get(sender()) == null) {
            self.doers.set(sender(), false);
            self.send_notification(self.owner, "You have a new candidate for the job.");
        }
    }

    get fun vacancies(): Cell? {
        return self.doers.asCell();
    }

    receive(msg: ChooseDoer) {
        self.requireOwner();
        require(self.state == self.OfferPublished, "Task is not published. ");
        require(self.doers.get(msg.doer) != null, "Doer is not registered. ");
        self.doers.set(msg.doer, true);
        self.doer = msg.doer;
        self.state = self.OfferAccepted;
        self.send_notification(self.doer!!, "You are accepted for the job.");
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
        if (msg.mark != null) {
            self.mark = msg.mark!!;
        }
        if (msg.review != null) {
            self.review = msg.review!!;
        }
        self.withdraw_deposit(self.doer!!, true);
    }
    receive(msg: Appeal) {
        require(self.on_appelation_by == null, "Only one appealation could be created");
        require(self.state == self.OfferAccepted || self.state == self.OfferCompleted, "Only for accepted or completed state.");
        require(self.doer == sender() || self.owner == sender(), "Only for doer or owner");
        let ctx: Context = context();
        require(ctx.value >= minGasCunsumption, "Not enough deposit. ");
        let init: StateInit = initOf AppealContract(myAddress(), msg.description);
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
        self.appeal_address = null;
        self.on_appelation_by = null;
        self.appeal_description = null;
        self.state = self.OfferCompleted;
        send(SendParameters{
            to: contractAddress(init),
            value: 0,
            mode: SendRemainingValue,
            body: Revoke{
                query_id: 0
                }.toCell()
        });
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
        send(SendParameters{
                to: self.native_wallet!!,
                value: ton("0.2"),
                body: WithdrawDeposit{
                    query_id: 0,
                    destination: address,
                    response_destination: address
                }.toCell(),
            });
        self.wallet_balance = 0;
        if (withFee) {
            let fee_amount: Int = self.jetton_balance * self.feePercent / 100000;
            send(SendParameters{
                to: self.jetton_wallet!!, 
                value: 0,
                mode: SendRemainingValue, 
                body: Transfer{ // 0x0f817ea5
                    query_id: 0,
                    amount: fee_amount,
                    destination: PlatformAddress,
                    response_destination: address,
                    custom_payload: beginCell().endCell(),
                    forward_ton_amount: ton("0.1"),
                    forward_payload: beginCell().endCell().asSlice(),
                }.toCell(),
                });
            self.jetton_balance = self.jetton_balance - fee_amount;
        }
        self.state = self.OfferClosed;
        send(SendParameters{
            to: self.jetton_wallet!!, 
            value: 0,
            mode: SendRemainingBalance, 
            body: Transfer{ // 0x0f817ea5
                query_id: 0,
                amount: self.jetton_balance,
                destination: address,
                response_destination: address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: ton("0.1"),
                forward_payload: beginCell().endCell().asSlice(),
            }.toCell(),
        });
        self.jetton_balance = 0;
    }

    get fun job_data(): ContractData {
        return ContractData{
            title: self.title,
            description: self.description,
            price: self.price,
            owner: self.owner,
            doer: self.doer,
            state: self.state,
            balance: myBalance(),
            jetton_wallet: self.jetton_wallet,
            native_wallet: self.native_wallet,
            jetton_balance: self.jetton_balance,
            wallet_balance: self.wallet_balance,
            appeal_address: self.appeal_address,
            mark: self.mark,
            review: self.review
        };
    }

    fun send_notification(address: Address, message: String) {
        send(SendParameters{
                to: address,
                value: 1,
                bounce: false,
                mode: SendPayGasSeparately | SendIgnoreErrors,
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
