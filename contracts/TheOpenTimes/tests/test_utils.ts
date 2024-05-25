import { Address, Contract, beginCell, toNano } from "@ton/core";
import { SandboxContract, TreasuryContract } from "@ton/sandbox";
import { TokenMaster } from "../wrappers/TokenMaster";
import { storeMint } from "../build/TokenMaster/tact_JobOffer";

let value_to_transfer: bigint = toNano(0.1)

export async function mint(
        master_owner: SandboxContract<TreasuryContract>, 
        master_contract: any, 
        receipient_address: Address, 
        amount: bigint
    ) {
    let result = await master_owner.send(
        {
            value: value_to_transfer,
            to: master_contract.address,
            body: beginCell().store(
                storeMint({
                    $$type: "Mint",
                    amount: amount,
                    receiver: receipient_address,
                    
                })
            ).endCell()
        }
    )
    return result
}


export async function deploy(deployer: SandboxContract<TreasuryContract>, contract: any) {
    await contract.send(
        deployer.getSender(),
        {
            value: toNano(value_to_transfer)
        },
        {
            $$type: "Deploy",
            query_id: 1n
        }
    )
}