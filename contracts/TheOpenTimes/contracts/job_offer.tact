import "./token_wallet";
import "./messages";
import "@stdlib/ownable";
import "@stdlib/deploy";

const forwardTonAmount: Int = 1;
const notificationAmount: Int = 1;
const minTonStorage: Int = ton("0.3");


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



struct JobOfferCloseState {
    doer: Bool;
    owner: Bool;
}

struct ContractData {
    title: String;
    description: String;
    price: Int as uint64;
    owner: Address;
    doer: Address?;
    state: Int as uint32;
    jetton_master: Address;
    balance: Int as coins;
    my_jetton_address: Address;
}

contract JobOffer with Deployable, Ownable {

    order: String;
    title: String;
    description: String;
    price: Int as coins;
    owner: Address;
    doer: Address?;
    job_state: JobOfferCloseState;
    state: Int;
    jetton_master: Address;
    const OfferCreated: Int = 0;
    const OfferPublished: Int = 1;
    const OfferAccepted: Int = 2;
    const OfferCompleted: Int = 3;
    const OfferConfirmed: Int = 4;
    const OfferAppelation: Int = 5;
    const OfferClosed: Int = 6;
    const TrackingAddress: Address = address("EQBYuxKgz-W5DeoBTgxaLgxGO9OHOVgjt-1qV0HGoQtp9_Wt");


    init(title: String, description: String, price: Int, order: String, jetton_master: Address) {
        self.title = title;
        self.description = description;
        self.price = price;
        self.order = order;
        self.jetton_master = jetton_master;
        self.owner = sender();
        self.job_state = JobOfferCloseState{doer: false, owner: false};
        self.state = self.OfferCreated;
        let ctx: Context = context();

        send(SendParameters{
            to: sender(), // sending message back to the sender
            value: ctx.value - minTonStorage, // don't add Toncoins to the message...
            body: self.order.asComment(),
        }); 

        // Skip Reason: cskip_no_gas
        send(SendParameters{
            to: self.TrackingAddress, // sending message back to the sender
            value: 0, 
            body: self.order.asComment(),
            mode: SendPayGasSeparately
        });
    }

    receive(msg: Revoke) {
        self.requireOwner();
        require(self.state == self.OfferPublished || self.state == self.OfferCreated, "Not for current state");
        self.send_deposit(self.owner, self.price);
        self.state = self.OfferClosed;
        send(SendParameters{
            to: sender(),
            value: 0,
            mode: SendRemainingBalance | SendDestroyIfZero,
            body: "Revoke job offer".asComment()
        });
    }

    receive(msg: Approve) {
        require(sender() == self.TrackingAddress, "Only for platform method");
        require(self.state == self.OfferCreated, "Invalid status for operation");
        if (msg.amount >= self.price) {
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
        self.send_notification(self.TrackingAddress, "Completed job.");
    }

    receive(msg: ConfirmJob) {
        self.requireOwner();
        require(self.state == self.OfferCompleted || self.state == self.OfferAccepted, "Only for completed or accepted state.");
        self.state = self.OfferClosed;
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);  
        let to: Address = contractAddress(init);
        send(SendParameters{
            to: to, 
            value: 0,
            mode: SendRemainingValue | SendIgnoreErrors | SendDestroyIfZero, 
            body: Transfer{ // 0x0f817ea5
                query_id: 0,
                amount: self.price,
                destination: self.doer!!,
                response_destination: self.owner,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: ton("0.1"),
                forward_payload: beginCell().endCell().asSlice(),
            }.toCell(),
            data: init.data,
            code: init.code,
        });
    }

    fun send_deposit(address: Address, amount: Int) {
        let ctx: Context = context();
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);  
        let to: Address = contractAddress(init);
        send(SendParameters{
            to: to, 
            value: 0,
            mode: SendRemainingValue | SendIgnoreErrors, 
            body: Transfer{ // 0x0f817ea5
                query_id: 0,
                amount: amount,
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
            owner: self.owner,
            doer: self.doer,
            state: self.state,
            jetton_master: self.jetton_master,
            balance: myBalance(),
            my_jetton_address: wallet_address
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

    receive(msg: Withdraw) {
        self.send_deposit(msg.to, msg.amount);
    }
}
